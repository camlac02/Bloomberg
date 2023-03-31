import sys
from classes.backtest_bloom import Backtester, Config, Frequency, TypeOptiWeights
# import blpapi
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
        TypeStrategy_strategie = TypeStrategy.Momentum
        if len(arr_options) != 2:
            "Il faut définir les lags pour la stratégie momentum"
        else: 
            df_otherdata = None
            int_lag1 = int(arr_options[0])
            int_lag2 = int(arr_options[1])
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.Size
        df_otherdata = None
        int_lag1 = None
        int_lag2 = None
    elif str_strategie == "btm":
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

    # File name initialisation following type of strategy and optimisation
    if TypeStrategy_strategie == TypeStrategy.Momentum:
        if TypeOptiWeights_optimisation == TypeOptiWeights.MAX_SHARPE:
            str_nomfichier = "_mom_maxs"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.MIN_VARIANCE:
            str_nomfichier = "_mom_minvar"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.RISK_PARITY:
            str_nomfichier = "_mom_risk"
    elif TypeStrategy_strategie == TypeStrategy.Size:
        if TypeOptiWeights_optimisation == TypeOptiWeights.MAX_SHARPE:
            str_nomfichier = "_mc_maxs"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.MIN_VARIANCE:
            str_nomfichier = "_mc_minvar"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.RISK_PARITY:
            str_nomfichier = "_mc_risk"
    elif TypeStrategy_strategie == TypeStrategy.Value:
        if TypeOptiWeights_optimisation == TypeOptiWeights.MAX_SHARPE:
            str_nomfichier = "_btm_maxs"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.MIN_VARIANCE:
            str_nomfichier = "_btm_minvar"
        elif TypeOptiWeights_optimisation == TypeOptiWeights.RISK_PARITY:
            str_nomfichier = "_btm_risk"
    
    with open('./JSON/json_back' + str_nomfichier + '.json') as file_f:
        json_back = json.load(file_f)

    with open('./JSON/json_dd' + str_nomfichier + '.json') as file_f:
        json_dd = json.load(file_f)
    
    with open('./JSON/json_mdd' + str_nomfichier + '.json') as file_f:
        json_mdd = json.load(file_f)

    with open('./JSON/json_values' + str_nomfichier + '.json') as file_f:
        json_values = json.load(file_f)

    with open('./JSON/json_tuw' + str_nomfichier + '.json') as file_f:
        json_tuw = json.load(file_f)

    with open('./JSON/json_perfs' + str_nomfichier + '.json') as file_f:
        json_perfs = json.load(file_f)

    print(json_back)
    print(json_dd)
    print(json_mdd)
    print(json_values)
    print(json_tuw)
    
    date_start = date_start[0:10]
    date_end = date_end[0:10]

    str_index = "^GSPC" if str_tickers == "SPX Index" else '^FCHI'
    cac = yf.download(str_index, start=date_start, end=date_end).Close
    df_cac = pd.DataFrame(100*cac/cac.iloc[0]).reset_index().to_dict('records')
    json_cac = json.dumps([{"ts": row["Date"].strftime("%Y-%m-%d"), "close": row["Close"]} for row in df_cac])
    
    print(json_cac)
    print(json_perfs)


def return_json(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options, str_frais):
    return (return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_optimisation, str_rebelancement, str_generic, str_options, str_frais))

if __name__ == '__main__':
    return_json(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10])
