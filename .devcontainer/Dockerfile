FROM python:3.11.4-slim-bullseye


RUN apt-get update && apt-get install -y git wget curl make python3-pip python3-venv python3-dev python3-pandas jq

COPY . /workspaces

WORKDIR /workspaces

# RUN ./build_helpers/install_ta-lib.sh

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    sed -i.bak "s|0.00000001|0.000000000000000001 |g" src/ta_func/ta_utility.h &&\
    ./configure --prefix=/usr/local --build=aarch64-unknown-linux-gnu &&\
    make &&\
    make install &&\
    # On debian based systems (debian, ubuntu, ...) - updating ldconfig might be necessary.
    ldconfig  &&\
    cd .. &&\ 
    rm -rf ./ta-lib* 

RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt --no-cache-dir
RUN python3 -m pip install -e .

CMD [ "freqtrade", "trade" ]