from freqtrade.persistence import Trade
from typing import Optional
import datetime
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class ClucMayBig3At(IStrategy):
    INTERFACE_VERSION = 3

    can_short: bool = False

    minimal_roi = {
        "0": 999
    }

    stoploss = -1
    trailing_stop = False

    exit_profit_only = True

    # DCA variables
    position_adjustment_enable = True

    bb_windows = IntParameter(10, 50, default=20, space='buy')
    bb_std = IntParameter(1, 3, default=2, space='buy')
    ema_window = IntParameter(30, 100, default=50, space='buy')
    cluc_mult = DecimalParameter(
        0.97, 1.2, default=0.985, decimals=3, space='buy', optimize=True)
    atr_window = IntParameter(10, 50, default=25, space='buy')
    atr_mult = DecimalParameter(-3, 3, decimals=1,
                                default=0.8, space='buy', optimize=True)

    # max_entry_position_adjustment = 3 # max safety order (1 base order + 3 safety order)
    max_epa = CategoricalParameter(
        [2, 3, 4, 5, 6, 7, 8, 9, 10], default=2, space='buy')

    # max_dca_multiplier = 5.5 # this for safety_order_volume_scale = 0.25
    safety_order_volume_scale = DecimalParameter(
        0.1, 1, decimals=2, default=0.25, space='buy')

    # safety_order_deviation = -0.08 # buy first safety order if profit -5%
    safety_order_deviation = DecimalParameter(
        -0.25, -0.01, decimals=2, default=-0.1, space='buy')

    # safety_order_step_scale = 1 # safety order step scale
    safety_order_step_scale = DecimalParameter(
        1, 5, decimals=1, default=1, space='buy')

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = True
    ignore_roi_if_entry_signal = False

    startup_candle_count: int = 50

    @property
    def max_entry_position_adjustment(self):
        return self.max_epa.value

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for window in self.atr_window.range:
            dataframe[f'atr_pct_{window}'] = ta.ATR(
                dataframe, timeperiod=window) / dataframe['close']
            for mult in self.atr_mult.range:
                dataframe[f'mult_{window}_{mult}'] = 1 - \
                    dataframe[f'atr_pct_{window}'] * mult

        for window in self.bb_windows.range:
            for std in self.bb_std.range:
                bollinger = qtpylib.bollinger_bands(
                    qtpylib.typical_price(dataframe), window=window, stds=std)
                dataframe[f'bb_lowerband_{window}_{std}'] = bollinger['lower']
                dataframe[f'bb_middleband_{window}_{std}'] = bollinger['mid']
                dataframe[f'bb_upperband_{window}_{std}'] = bollinger['upper']

        for window in self.ema_window.range:
            dataframe[f'ema_{window}'] = ta.EMA(dataframe, timeperiod=window)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe[f'ema_{self.ema_window.value}']) &
                (dataframe['close'] < (self.cluc_mult.value * dataframe[f'mult_{self.atr_window.value}_{self.atr_mult.value}']) * dataframe[f'bb_lowerband_{self.bb_windows.value}_{self.bb_std.value}']) &
                (dataframe['volume'] < (dataframe['volume'].rolling(
                    window=30).mean().shift(1) * 20))
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] >
                 dataframe[f'bb_middleband_{self.bb_windows.value}_{self.bb_std.value}'])
            ),
            'exit_long'] = 1

        return dataframe

    # This is called when placing the initial order (opening trade)
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:

        max_dca_multiplier = (
            1+(1+(self.safety_order_volume_scale.value*self.max_epa.value))) * ((self.max_epa.value+1)/2)
        return proposed_stake / max_dca_multiplier

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:

        filled_entries = trade.select_filled_orders(trade.entry_side)
        count_of_entries = trade.nr_of_successful_entries
        count_of_safety_order = count_of_entries-1

        if current_profit > self.safety_order_deviation.value*(self.safety_order_step_scale.value**count_of_safety_order):
            return None

        # Obtain pair dataframe (just to show how to access it)
        dataframe, _ = self.dp.get_analyzed_dataframe(
            trade.pair, self.timeframe)
        # Only buy when not actively falling price.
        last_candle = dataframe.iloc[-1].squeeze()
        previous_candle = dataframe.iloc[-2].squeeze()
        if last_candle['close'] < previous_candle['close']:
            return None

        try:
            # This returns first order stake size
            stake_amount = filled_entries[0].cost
            # This then calculates current safety order size
            stake_amount = stake_amount * \
                (1 + (count_of_entries * self.safety_order_volume_scale.value))
            return stake_amount
        except Exception as exception:
            return None
