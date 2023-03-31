import sys
import sys
import subprocess
from classes.backtest_bloom import Backtester, Config, Frequency, TypeOptiWeights
import blpapi
import json
import datetime as dt
import yfinance as yf
import numpy as np
import pandas as pd
from classes.module import BLP
from classes.strategies_bloom import Strategies, TypeStrategy
import matplotlib.pyplot as plt

def return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options):
    arr_tickers = str_tickers.split(", ")
    arr_fields = str_fields.split(", ")
    arr_options = str_options.split(", ")

    if str_rebelancement != "":
        int_rebalancement = int(str_rebelancement)
    else :
        int_rebalancement = 10
    if str_generic == 'True':
        bool_generic = True
    else:
        bool_generic = False

    # Strategy type definition
    if str_strategie == "Momentum":
        TypeStrategy_strategie = TypeStrategy.Momentum
        if len(arr_options) != 2:
            "Il faut définir les lags pour la stratégie momentum"
        else:
            df_otherdata = None
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
    elif str_strategie == "Size":
        TypeStrategy_strategie = TypeStrategy.Size
        df_otherdata = None
        int_lag1 = None
        int_lag2 = None
    elif str_strategie == "Value":
        TypeStrategy_strategie = TypeStrategy.Value
        if len(arr_options) != 3:
            "Il faut définir les lags et l'autre type de data pour la stratégie book-to-market"
        else:
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
            str_otherdata = arr_options[2]
    else :
        return "La stratégie n'est pas définie"

    if str_optimisation == "max_sharpe":
        TypeOptiWeights_optimisation = TypeOptiWeights.MAX_SHARPE
    elif str_optimisation == "min_variance":
        TypeOptiWeights_optimisation = TypeOptiWeights.MIN_VARIANCE
    elif str_optimisation == "risk_parity":
        TypeOptiWeights_optimisation = TypeOptiWeights.RISK_PARITY
    else:
        return "Le type d'optimisation n'est pas défini"

    DATE = blpapi.Name("date")
    ERROR_INFO = blpapi.Name("errorInfo")
    EVENT_TIME = blpapi.Name("EVENT_TIME")
    FIELD_DATA = blpapi.Name("fieldData")
    FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
    FIELD_ID = blpapi.Name("fieldId")
    SECURITY = blpapi.Name("security")
    SECURITY_DATA = blpapi.Name("securityData")

    blp = BLP(DATE, SECURITY, SECURITY_DATA, FIELD_DATA)
    dic_compo = blp.compo_per_date_old(strSecurity=arr_tickers, strFields=arr_fields,
                     strOverrideField="END_DATE_OVERRIDE", strOverrideValue=date_start, strEndDate=date_end)
    df_index = pd.DataFrame(dic_compo).T
    list_index = list(map(lambda x: x + " Equity", sorted(list(set(df_index.sum()[0])))))

    dic_tickers = {k: list(map(lambda x: x + " Equity", np.array(v).flatten().tolist())) for k, v in dic_compo.items()}
    df_history = blp.bdh(list_index, ['PX_LAST'], date_start, date_end)

    if str_strategie == TypeStrategy.Value.value:
        df_otherdata = blp.bdh(list_index, [str_otherdata], date_start, date_end)

    configuration = Config(universe=list_index, start_ts=date_start, end_ts=date_end,
                           strategy_code=TypeStrategy_strategie.value, name_index=arr_tickers,
                           frequency=Frequency.DAILY)
    Backtester_backtest = Backtester(config=configuration, data=df_history, compo=dic_tickers,
                          intReshuffle=int_rebalancement, boolGeneric=bool_generic, lag1=int_lag1, lag2=int_lag2,
                          strat=TypeOptiWeights_optimisation, other_data = df_otherdata, fees=0.002)

    df_back = Backtester_backtest.compute_levels()

    df_backtester = pd.DataFrame(df_back)
    plt.plot(df_backtester.ts, df_backtester.close)
    plt.xlabel('Date')
    plt.ylabel('Portfolio value')
    plt.title('Evolution portfolio')
    plt.show()
    blp.closeSession()

def return_json(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options):
    (return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options))

if __name__ == '__main__':
    return_json("PX_LAST, INDX_MWEIGHT_HIST", "CAC Index", dt.datetime(2015, 1, 2), dt.datetime(2023, 1, 5), "Momentum", "max_sharpe", '22', 'False', '25, 250')
    # return_json(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
   # sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9]