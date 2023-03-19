# API Bloomberg

pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi

The last update files:

- gene: generate a random data set. Used to test the stability of the strategies.

- main_bloom: main which used the Bloomberg API. It will be our final main.

- backtest_bloom: backtest adapted to the Bloomberg API. It will be our final backtest.

- generic_syntethic_data: same as gene but integrated in the class file. DO NOT DELETE: Still has to make it adaptable
  to BLP API

- strategies_bloomberg: slighly changes compared to the other script. I only keep the other one to keep alive the scripts
  which are running without using the BLP API
