import sys
from classes.backtest_bloom import Backtester, Config, Frequency, TypeOptiWeights
import blpapi
import json
import datetime as dt
import yfinance as yf
import numpy as np
import pandas as pd
from classes.module import BLP
from classes.strategies_bloom import Strategies, TypeStrategy

def return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options, str_frais):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    arr_options = str_options.split(", ") 

    if str_rebelancement != "":
        int_rebalancement = int(str_rebelancement)
    else :
        int_rebalancement = 10

    if str_frais != "":
        float_frais = float(str_frais)
    else :
        float_frais = 0

    if str_generic == 'True':
        bool_generic = True
    else:
        bool_generic = False 

    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
        if len(arr_options) != 2:
            "Il faut définir les lags pour la stratégie momentum"
        else: 
            df_otherdata = None
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
        df_otherdata = None
        int_lag1 = None
        int_lag2 = None
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
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

    if str_strategie == TypeStrategy.btm.value:
        df_otherdata = blp.bdh(list_index, [str_otherdata], date_start, date_end)

    configuration = Config(universe=list_index, start_ts=date_start, end_ts=date_end,
                           strategy_code=TypeStrategy_strategie.value, name_index=arr_tickers, 
                           frequency=Frequency.DAILY)
    Backtester_backtest = Backtester(config=configuration, data=df_history, compo=dic_tickers,
                          intReshuffle=int_rebalancement, boolGeneric=bool_generic, lag1=int_lag1, lag2=int_lag2, 
                          strat=TypeOptiWeights_optimisation, other_data = df_otherdata)
    df_back = Backtester_backtest.compute_levels()

    # Loop on each element of backtester object to format json
    dict_quotes = []
    for quote in df_back:
        dict_quote = {'ts': quote.ts.isoformat(), 'close': quote.close}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_back = json.dumps(dict_quotes)
    print(json_back)

    df_backtester = pd.DataFrame(df_back)
    int_max = df_backtester['close'].cummax()
    serie_dd = df_backtester['close'] / int_max - 1.0
    df_dd = pd.DataFrame(serie_dd)
    df_mdd = pd.DataFrame(serie_dd.cummin())

    # Loop on each element of drawdown dataframe object to format json
    dict_quotes = []
    for int_element in range(len(df_dd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'drawdown': df_dd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    json_dd = json.dumps(dict_quotes)
    print(json_dd)

    # Loop on each element of maximum drawdown dataframe object to format json
    dict_quotes = []
    for int_element in range(len(df_mdd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'mdd': df_mdd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    json_mdd = json.dumps(dict_quotes)
    print(json_mdd)

    # Historical VaR, hit ratio, Mean return from hits, Mean return from misses
    ret = df_backtester.close.pct_change().dropna().sort_values().reset_index(drop=True)
    float_VaR = round(ret[int((1-0.95) * ret.shape[0])-1], 2)
    float_hitratio = round(Backtester_backtest.dictHitStat['hit'] / Backtester_backtest.dictHitStat['total_position_taken'], 2)
    float_meanhits = round(Backtester_backtest.dictHitStat['mean_ret_from_hits'], 5)
    float_meanmisses = round(Backtester_backtest.dictHitStat['mean_ret_from_misses'], 5)
    
    # Loop on each element of backtester object to format json
    arr_values = [float_VaR, float_hitratio, float_meanhits, float_meanmisses]
    arr_names = ["Value-at-risk", "Hit ratio", "Mean return from hits", "Mean return from misses"]
    dict_quotes = []
    for int_element in range(len(arr_values)):
        dict_quote = {'variable': arr_names[int_element], 'value': arr_values[int_element]}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_values = json.dumps(dict_quotes)
    print(json_values)

    dict_quotes = []
    arr_tuw = Backtester_backtest.tuw.copy()
    for int_tuw in range(len(arr_tuw)):
        dict_quote = {'ts': arr_tuw.index[int_tuw].isoformat(), 'tuw': arr_tuw[int_tuw].days}
        dict_quotes.append(dict_quote)

    json_tuw = json.dumps(dict_quotes)
    print(json_tuw)

    dfRet = df_backtester['close'].pct_change()
    std_daily = 100*np.std(dfRet) / np.sqrt(int_rebalancement)
    # std_daily = np.std(daily_returns)*100

    total_return = (df_backtester.close.iloc[-1] / df_backtester.close.iloc[0]) - 1
    annualized_perf = (1 + total_return) ** (1 / ((date_end-date_start).days/365)) - 1 # false

    # Loop on each element of backtester object to format json
    arr_values = [round(std_daily, 2), round(std_daily * np.sqrt(22), 2), round(std_daily * np.sqrt(252), 2), round(annualized_perf*100, 2), round(total_return*100, 2)]
    arr_names = ["Daily Vol %", "Monthly Vol %", "Annualized Vol %", "Annualized Perf %", "Overall Perf %"]
    dict_quotes = []
    for int_element in range(len(arr_values)):
        dict_quote = {'variable': arr_names[int_element], 'value': arr_values[int_element]}
        dict_quotes.append(dict_quote)

    json_stats = json.dumps(dict_quotes)

    # Create output PORT from dict
    dfOutputPort = pd.DataFrame.from_dict(Backtester_backtest._weight_by_pk, orient='index', columns=["ts", "underlying_code",'value'] ,dtype=None)
    dfOutputPort.index = pd.MultiIndex.from_tuples(dfOutputPort.index)
    factor = dfOutputPort.index.get_level_values(0)
    dfOutputPort['Factor'] = factor.to_numpy()
    dfOutputPort.reset_index(inplace=True, drop=True)
    # polars to int
    dfOutputPort['value'] = dfOutputPort['value'].apply(lambda x: x.to_numpy()[0][0])

    cac = yf.download('^FCHI', start=date_start, end=date_end).Close
    df_cac = pd.DataFrame(100*cac/cac.iloc[0]).reset_index().to_dict('records')
    json_cac = json.dumps([{"ts": row["Date"].strftime("%Y-%m-%d"), "close": row["Close"]} for row in df_cac])

    print(json_cac)
    print(json_stats)


def return_json(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options, str_frais):
    return (return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options, str_frais))

if __name__ == '__main__':
    return_json(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])