import datetime

import matplotlib.pyplot as plt

from classes.backtest import Backtester, Config, Frequency
import blpapi
import numpy as np
import pandas as pd
import datetime as dt
from classes.module import BLP
from classes.strategies import Strategies
import polars as pl

if __name__ == '__main__':
    DATE = blpapi.Name("date")
    ERROR_INFO = blpapi.Name("errorInfo")
    EVENT_TIME = blpapi.Name("EVENT_TIME")
    FIELD_DATA = blpapi.Name("fieldData")
    FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
    FIELD_ID = blpapi.Name("fieldId")
    SECURITY = blpapi.Name("security")
    SECURITY_DATA = blpapi.Name("securityData")

    blp = BLP(DATE, SECURITY, SECURITY_DATA, FIELD_DATA)
    strFields = ["PX_LAST", "INDX_MEMBERS"]
    tickers = ["CAC Index"]
    startDate = dt.datetime(2019, 10, 1)
    endDate = dt.datetime(2020, 11, 3)
    # bloom = blpp.bds(tickers=tickers, flds=strFields, startDate= startDate, endDate= endDate)
    bloom2 = blp.bds(strSecurity=tickers, strFields=strFields, strOverrideField='PiTDate', strOverrideValue='20101001') # do not run ==> still trying to get historical values
    list_index = list(map(lambda x: x + " Equity", bloom2['INDX_MEMBERS'][tickers[0]]))

    # data = blp.bdh(list_index[:3], ['PX_LAST'], startDate, endDate) # CUR_MKT_CAP
    data = pd.read_csv('data/data_blp.csv', index_col=0).dropna(axis=1)
    list_index = data.columns
    data.index = pd.to_datetime(data.index)


    # création momentum data
    strat = Strategies()
    strat.momentum(data, 5, 25)
    strat.momentum_data.reset_index(inplace=True)
    strat.momentum_data.rename(columns ={"index":'Date'}, inplace=True)
    data.reset_index(inplace=True)
    data.rename(columns ={"index":'Date'}, inplace=True)
    df = data[data.Date >= strat.momentum_data['Date'][0]]

    # création d'un index syntethic
    df_compo_index_ts = pd.DataFrame(np.zeros((data.shape[0]-25,2)), columns=['Date','Compo'])
    df_compo_index_ts['Date'] = data.Date[25:].to_numpy()
    df_compo_index_ts['Compo'] = [data.columns[1:].to_list() for _ in range(len(df_compo_index_ts))]


    configuration = Config(universe=list_index,
                           start_ts=strat.momentum_data.Date.iloc[0],
                           end_ts=strat.momentum_data.Date.iloc[-1],
                           strategy_code='momentum',
                           frequency=Frequency.DAILY,
                           timeserie=strat.momentum_data)
    backtest = Backtester(config=configuration, strat_data= pl.convert.from_pandas(strat.momentum_data),
                          timeserie=pl.convert.from_pandas(df),
                          compo=df_compo_index_ts,
                          reshuffle=10)
    back = pd.DataFrame(backtest.compute_levels())
    plt.plot(back['ts'], back['close'])
    plt.xlabel('date')
    plt.ylabel('ptf level')
    plt.title('ptf evolution - momentum')
    plt.legend()
    plt.show()