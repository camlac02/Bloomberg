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
    type_strat = TypeStrategy.btm.value
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
    startDate = dt.datetime(2020, 1, 2)
    endDate = dt.datetime(2023, 2, 10)

    dictCompoIndex = blp.compo_per_date_old(strSecurity=tickers, strFields=strFields,
                                            strOverrideField="END_DATE_OVERRIDE", strOverrideValue=startDate,
                                            strEndDate=endDate)
    idx_df = pd.DataFrame(dictCompoIndex).T
    unique_idx = sorted(list(set(idx_df.sum()[0])))
    list_index = list(map(lambda x: x + " Equity", unique_idx))

    dictTickersTime = {k: list(map(lambda x: x + " Equity", np.array(v).flatten().tolist())) for k, v in
                   dictCompoIndex.items()}
    dfHistory = blp.bdh(list_index, ['TOTAL_EQUITY'], startDate, endDate)  # CUR_MKT_CAP # TOT_COMMON_EQY # PX_LAST
    if type_strat == TypeStrategy.btm.value:
        dfHistory_btm = blp.bdh(list_index, ['CUR_MKT_CAP'], startDate, endDate)
    else:
        dfHistory_btm =None
    configuration = Config(universe=list_index,
                           start_ts=startDate,
                           end_ts=endDate,
                           strategy_code=type_strat,
                           name_index=tickers,
                           frequency=Frequency.DAILY)

    backtest = Backtester(config=configuration, data=dfHistory,
                          compo=dictTickersTime,
                          intReshuffle=10,
                          lag1=30, lag2=200, boolGeneric=False, strat=TypeOptiWeights.MIN_VARIANCE,
                          other_data=dfHistory_btm)

    back = backtest.compute_levels()
    backtest_res = pd.DataFrame(back)
    plt.figure(1)
    plt.plot(backtest_res['ts'], backtest_res['close'])
    plt.xlabel('date')
    plt.ylabel('ptf level')
    plt.title('ptf evolution - momentum')
    plt.legend()

    import yfinance as yf

    cac = yf.download('^FCHI', start=backtest.config.start_ts, end=backtest.config.end_ts).Close
    cac = 100 * cac / cac.iloc[0]
    plt.plot(cac)
    plt.show()

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
    hist_level_index = int((1 - level_VaR) * ret.shape[0])
    historical_VaR = round(ret[hist_level_index - 1], 2)

    #

    # hit ratios

    hit_ratio_total = round(backtest.dictHitStat['hit'] / backtest.dictHitStat['total_position_taken'], 2)
    mean_ret_from_hits = round(backtest.dictHitStat['mean_ret_from_hits'], 5)
    mean_ret_from_misses = round(backtest.dictHitStat['mean_ret_from_misses'], 5)

    # TuW
    tuw = backtest.tuw
    dd = backtest.dd
    #
    # s = blp.BDS("CAC Index", "INDX_MWEIGHT_HIST")
    # blp.closeSession()
