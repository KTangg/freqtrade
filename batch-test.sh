 
#!/bin/bash

TIMERANGE="20230101-20231201"
# "20170101-20230420"
# 20220120-20231020 (stress test)

HYPEROPT_TIMERANGE="20170101-20231215"

BASE_PATH="user_data/stock_hyperopt"

STRATEGY_PATH="${BASE_PATH}/strategies"

tf=("15m" "1h" "4h" "1d")

STRATEGY=(
    "ClucMayBig3At"
    # "ClucMayBig3"
    # "ClucMayBig5Mo2"
    # "ClucMayBig5Mo3"
    # "ClucMayTop10Mo1"
    # "ClucMayTop10Mo2"
    # "ClucMayTop10Mo3"
    # "DonchainBig5CaMo1"
    # "DonchainBig5CaMo2"
    # "DonchainBig5PoMo1"
    # "DonchainBig5PoMo2"
    # "DoubleBandBig5Mo1"
    # "DoubleBandBig5Mo2"
    # "DoubleBandTop10DdMo1"
    # "DoubleBandTop10DdMo2"
    # "DoubleBandTop10DdMo3"
    # "DoubleBandTop10Mo1"
    # "DoubleBandTop10Mo2"
    # "DoubleBandTop10Mo3"
    # "EmaPumpTop10Po"
    # "EmaPumpTop10"
    # "KeltnerTop10Mo4"
    # "LinearCloudTop10Mo1"
    # "LinearCloudTop10Mo2"
    # "LinearCloudTop10Mo3"
    # "RelativeMacdBig3"
    # "RelativeMacdBig3At"
    # "RelativeMacdBig5Mo1"
    # "RelativeMacdBig5Mo2"
    # "RelativeMacdTop10Mo1"
    # "RelativeMacdTop10Mo2"
    # "RelativeMacdTop10Mo3"
    # "SuperDoubleBandBig3"
    # "SuperDoubleBandBig3At"
    # "SuperClucBig3"
    # "SuperClucBig3At"
    # "SuperClucTop10Tb"
    # "SuperNimbusTop10DdMo2"
    # "VWAPBig3"
)

CONFIG=(
    "config-clucmay_big3_at.json"
    # "config-clucmay_big3.json"
    # "config-clucmay_big5_mo2.json"
    # "config-clucmay_big5_mo3.json"
    # "config-clucmay_top10_mo1.json"
    # "config-clucmay_top10_mo2.json"
    # "config-clucmay_top10_mo3.json"
    # "config-donchain_big5_ca_mo1.json"
    # "config-donchain_big5_ca_mo2.json"
    # "config-donchain_big5_po_mo1.json"
    # "config-donchain_big5_po_mo2.json"
    # "config-doubleband_big5_mo1.json"
    # "config-doubleband_big5_mo2.json"
    # "config-doubleband_top10_dd_mo1.json"
    # "config-doubleband_top10_dd_mo2.json"
    # "config-doubleband_top10_dd_mo3.json"
    # "config-doubleband_top10_mo1.json"
    # "config-doubleband_top10_mo2.json"
    # "config-doubleband_top10_mo3.json"
    # "config-emapump_top10_po.json"
    # "config-emapump_top10.json"
    # "config-keltner_top10_mo4.json"
    # "config-linearcloud_top10_mo1.json"
    # "config-linearcloud_top10_mo2.json"
    # "config-linearcloud_top10_mo3.json"
    # "config-relative_macd_big3.json"
    # "config-relative_macd_big3_at.json"
    # "config-relative_macd_big5_mo1.json"
    # "config-relative_macd_big5_mo2.json"
    # "config-relative_macd_top10_mo1.json"
    # "config-relative_macd_top10_mo2.json"
    # "config-relative_macd_top10_mo3.json"
    # "config-super_doubleband_big3.json"
    # "config-super_doubleband_big3_at.json"
    # "config-supercluc_big3.json"
    # "config-supercluc_big3_at.json"
    # "config-supercluc_top10_tb.json"
    # "config-supernimbus_top10_dd_mo2.json"
    # "config-vwap_big3.json"
)

mkdir -p user_data/mass_test_result/backtest_summary
mkdir -p user_data/mass_test_result/backtest_result
rm -rf user_data/mass_test_result/backtest_summary/*
rm -rf user_data/mass_test_result/backtest_result/*

 
for ((i = 0; i < ${#STRATEGY[@]}; i++)); do
    docker run --rm -v $(pwd)/user_data:/freqtrade/user_data freqtradeorg/freqtrade backtesting --breakdown month \
        --strategy ${STRATEGY[i]} --timerange $TIMERANGE --strategy-path $STRATEGY_PATH \
        --config ${BASE_PATH}/${CONFIG[i]} --export-filename user_data/mass_test_result/backtest_result/${STRATEGY[i]}.json \
        >user_data/mass_test_result/backtest_summary/${STRATEGY[i]}.txt
#   docker run --rm  -v ./user_data:/freqtrade/user_data interactive-trade hyperopt --timerange 20220101-20230101 --timeframe 1d --strategy ClucMayStrategy --hyperopt-loss SharpeHyperOptLoss -e 100 --space buy -j 1
done



