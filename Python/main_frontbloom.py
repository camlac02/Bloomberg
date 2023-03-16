import sys
import subprocess
from functools import reduce
import matplotlib.pyplot as plt
from classes.backtest_bloom import Backtester, Config, Frequency, TypeOptiWeights
import blpapi
import yfinance as yf
import json
import numpy as np
import pandas as pd
import datetime as dt
from classes.module import BLP
from classes.strategies_bloom import Strategies, TypeStrategy

# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polars'])
import polars as pl

def return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_options):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    arr_options = str_options.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
        if len(arr_options) != 2:
            "Il faut définir les lags pour la stratégie momentum"
        else: 
            data_other = None
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
        if len(arr_options) != 0:
            "Il ne faut pas d'options pour la stratégie market capitalization"
        else: 
            data_other = None
            int_lag1 = None
            int_lag2 = None
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
        if len(arr_options) != 3:
            "Il faut définir les lags et l'autre type de data pour la stratégie book-to-market"
        else: 
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
            data_other = arr_options[2]
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
    bloom2 = blp.compo_per_date_old(strSecurity=arr_tickers, strFields=arr_fields,
                     strOverrideField="END_DATE_OVERRIDE", strOverrideValue=date_start, strEndDate=date_end)
    df_index = pd.DataFrame(bloom2).T
    list_index = list(map(lambda x: x + " Equity", sorted(list(set(df_index.sum()[0])))))

    bloom = {k: list(map(lambda x: x + " Equity", np.array(v).flatten().tolist())) for k, v in bloom2.items()}
    data = blp.bdh(list_index, ['PX_LAST'], date_start, date_end) 
    
    configuration = Config(universe=list_index, start_ts=date_start, end_ts=date_end,
                           strategy_code=TypeStrategy_strategie.value, name_index=arr_tickers, 
                           frequency=Frequency.DAILY)
    Backtester_backtest = Backtester(config=configuration, data=data, compo=bloom,
                          reshuffle=10, generic=True, lag1=int_lag1, lag2=int_lag2, strat=TypeOptiWeights_optimisation)
    df_back = Backtester_backtest.compute_levels()

    # Loop on each element of backtester object to format json
    dict_quotes = []
    for quote in df_back:
        dict_quote = {'ts': quote.ts.isoformat(), 'close': quote.close}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_back = json.dumps(dict_quotes)

    df_backtester = pd.DataFrame(df_back)
    int_max = df_backtester['close'].cummax()
    serie_dd = df_backtester['close'] / int_max - 1.0
    df_dd = pd.DataFrame(serie_dd)
    df_mdd = pd.DataFrame(serie_dd.cummin())

    # Loop on each element of drawdown dataframe object to format json
    for int_element in range(len(df_dd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'drawdown': df_dd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    json_dd = json.dumps(dict_quotes)

    # Loop on each element of maximum drawdown dataframe object to format json
    for int_element in range(len(df_mdd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'mdd': df_mdd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    json_mdd = json.dumps(dict_quotes)

    # Historical VaR
    ret = df_backtester.close.pct_change().dropna().sort_values().reset_index(drop=True)
    float_VaR = round(ret[int((1-0.95) * ret.shape[0])-1], 2)
    float_hitratio = round(Backtester_backtest.hit_dict['hit'] / Backtester_backtest.hit_dict['total_position_taken'], 2)
    float_meanhits = round(Backtester_backtest.hit_dict['mean_ret_from_hits'], 5)
    float_meanmisses = round(Backtester_backtest.hit_dict['mean_ret_from_misses'], 5)
    
    # Loop on each element of backtester object to format json
    arr_values = [float_VaR, float_hitratio, float_meanhits, float_meanmisses]
    arr_names = ["float_VaR", "float_hitratio", "float_meanhits", "float_meanmisses"]
    for int_element in range(len(arr_values)):
        dict_quote = {'variable': arr_names[int_element], 'value': arr_values[int_element]}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_values = json.dumps(dict_quotes)

    with open('json_back_mc_minvar.json', 'w') as f:
        json.dump(json_back, f)

    with open('json_dd_mc_minvar.json', 'w') as f:
        json.dump(json_dd, f)

    with open('json_mdd_mc_minvar.json', 'w') as f:
        json.dump(json_mdd, f)

    with open('json_values_mc_minvar.json', 'w') as f:
        json.dump(json_values, f)

    return json_back, json_dd, json_mdd, json_values

if __name__ == '__main__':
    return_values('PX_LAST, INDX_MWEIGHT_HIST', 'CAC Index', dt.datetime(2015, 1, 1), dt.datetime(2023, 2, 10), 'momentum', 'min_variance', '5, 25')