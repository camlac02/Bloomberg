import sys
import subprocess
from functools import reduce
import matplotlib.pyplot as plt
from classes.backtest_bloom import Backtester, Config, Frequency, TypeOptiWeights
import blpapi
import numpy as np
import pandas as pd
import datetime as dt
from classes.module import BLP
from classes.strategies_bloom import Strategies, TypeStrategy

# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polars'])
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
    strFields = ["PX_LAST", "INDX_MWEIGHT_HIST"]
    tickers = ["CAC Index"]
    startDate = dt.datetime(2015, 1, 1)
    endDate = dt.datetime(2019, 12, 3)
    bloom21 = blp.bds(strSecurity=tickers, strFields=strFields,
                     strOverrideField="END_DATE_OVERRIDE", strOverrideValue=dt.datetime.strftime(startDate, "%Y%m%d"))
    bloom2 = blp.compo_per_date_old(strSecurity=tickers, strFields=strFields,
                     strOverrideField="END_DATE_OVERRIDE", strOverrideValue=startDate, strEndDate=endDate)
    idx_df = pd.DataFrame(bloom2).T
    unique_idx = sorted(list(set(idx_df.sum()[0])))
    list_index = list(map(lambda x: x + " Equity", unique_idx))
    #list_index2 = list(map(lambda x: x + " Equity", bloom2['INDX_MWEIGHT_HIST'][tickers[0]]))

    bloom = {k: list(map(lambda x: x + " Equity", np.array(v).flatten().tolist())) for k, v in bloom2.items()}
    data = blp.bdh(list_index, ['PX_LAST'], startDate, endDate) # CUR_MKT_CAP # TOT_COMMON_EQY # PX_LAST
    # data.to_csv('data_blp.csv')
    #data = pd.read_csv('data/data_blp.csv', index_col=0).dropna(axis=1)
    #list_index = data.columns
    #data.index = pd.to_datetime(data.index)
    #data.sort_index(inplace=True)

    # momentum data
    #strat = Strategies(TypeStrategy.momentum)
    #strat.data_strategies(data.copy(), 5, 25)

    # keep only data we are interested in
    #data.reset_index(inplace=True)
    #data.rename(columns={"index": 'Date'}, inplace=True)
    #df = data[data.Date >= strat.strat_data['Date'][0]]

    # compo index syntethic: will not be in the final code
    #df_compo_index_ts = pd.DataFrame(np.zeros((strat.strat_data.shape[0],2)), columns=['Date','Compo'])
    #df_compo_index_ts['Date'] = strat.strat_data['Date']
    #df_compo_index_ts['Compo'] = [strat.strat_data.columns[1:].to_list() for _ in range(len(df_compo_index_ts))]

    #bloom = {(df_compo_index_ts['Date'][0], 'CAC Index'): df_compo_index_ts['Compo'][0][:40],
    #         (df_compo_index_ts['Date'][5], 'CAC Index'): df_compo_index_ts['Compo'][5][10:50],
    #         (df_compo_index_ts['Date'][10], 'CAC Index'): df_compo_index_ts['Compo'][50][:40]}

    #return_mat = data.copy()
    #return_mat.iloc[:, 1:] = return_mat.iloc[:, 1:].pct_change()
    #return_mat.Date = return_mat.Date.astype('datetime64')

    configuration = Config(universe=list_index,
                           start_ts=startDate,
                           end_ts=endDate,
                           strategy_code=TypeStrategy.mc.value,
                           name_index=tickers,
                           frequency=Frequency.DAILY)
    backtest = Backtester(config=configuration, data=data,
                          compo=bloom,
                          reshuffle=10,
                          lag1=None, lag2=None, generic=True, strat=TypeOptiWeights.MIN_VARIANCE)

    back = backtest.compute_levels()
    backtest_res = pd.DataFrame(back)
    plt.figure(1)
    plt.plot(backtest_res['ts'], backtest_res['close'])
    plt.xlabel('date')
    plt.ylabel('ptf level')
    plt.title('ptf evolution - momentum')
    plt.legend()
    plt.show()
    import yfinance as yf
    cac =yf.download('^FCHI', start=strat.strat_data.Date.iloc[0], end=strat.strat_data.Date.iloc[-1]).Close
    cac = 100*cac/cac.iloc[0]
    plt.plot(cac)

    # Daily drawdown
    plt.figure(2)
    Roll_Max = backtest_res['close'].cummax()
    Daily_Drawdown = backtest_res['close'] / Roll_Max - 1.0
    Max_Daily_Drawdown = Daily_Drawdown.cummin()
    plt.plot(backtest_res['ts'], Max_Daily_Drawdown)
    plt.xlabel('date')
    plt.ylabel('Max Drawdown in %')
    plt.title('Drawdowns through time')
    plt.legend()
    plt.show()

    # Historical VaR in percentage: -0.86 means that the ptf went down by 86%
    level_VaR = 0.95
    ret = backtest_res.close.pct_change().dropna().sort_values().reset_index(drop=True)
    hist_level_index = int((1-level_VaR) * ret.shape[0])
    historical_VaR = round(ret[hist_level_index-1], 2)

    #

    # hit ratios

    hit_ratio_total = round(backtest.hit_dict['hit'] / backtest.hit_dict['total_position_taken'], 2)
    mean_ret_from_hits = round(backtest.hit_dict['mean_ret_from_hits'], 5)
    mean_ret_from_misses = round(backtest.hit_dict['mean_ret_from_misses'], 5)

    # TuW
    tuw = backtest.tuw
    dd = backtest.dd
    #
    #s = blp.BDS("CAC Index", "INDX_MWEIGHT_HIST")
    # blp.closeSession()
