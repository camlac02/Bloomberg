import sys
import subprocess
import json
from classes.backtest_save import Backtester, Config, Frequency
import numpy as np
import pandas as pd
import datetime as dt
from classes.strategies import Strategies, TypeStrategy
import polars as pl

def json_close(str_fields, str_tickers, date_start, date_end, str_strategie):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
    else :
        return "La stratégie n'est pas définie"

    # Retrieval of data obtained from Bloomberg
    df_data = pd.read_csv('./Python/data/generic.csv', index_col=0).dropna(axis=1)
    list_index = df_data.columns
    df_data.index = pd.to_datetime(df_data.index)
    df_data.sort_index(inplace=True)

    # Strategy definition
    TypeStrategy_strat = Strategies(TypeStrategy_strategie)
    TypeStrategy_strat.data_strategies(df_data.copy(), 5, 25)

    # Keep only data we are interested in
    df_data.reset_index(inplace=True)
    df_data.rename(columns={"index": 'Date'}, inplace=True)
    df = df_data[df_data.Date >= TypeStrategy_strat.strat_data['Date'][0]]

    # Composition of syntethic index
    df_compo = pd.DataFrame(np.zeros(
        (TypeStrategy_strat.strat_data.shape[0], 2)), columns=['Date', 'Compo'])
    df_compo['Date'] = TypeStrategy_strat.strat_data['Date']
    df_compo['Compo'] = [TypeStrategy_strat.strat_data.columns[1:].to_list()
                         for _ in range(len(df_compo))]

    dic_bloom = {(df_compo['Date'][0], 'CAC Index'): df_compo['Compo'][0][:40],
                 (df_compo['Date'][5], 'CAC Index'): df_compo['Compo'][5][10:50],
                 (df_compo['Date'][10], 'CAC Index'): df_compo['Compo'][50][:40]}

    # Calculation percentage return rate
    df_return = df_data.copy()
    df_return.iloc[:, 1:] = df_return.iloc[:, 1:].pct_change()

    Config_configuration = Config(universe=list_index, start_ts=TypeStrategy_strat.strat_data.Date.iloc[0],
                                  end_ts=TypeStrategy_strat.strat_data.Date.iloc[-1], strategy_code=TypeStrategy_strategie.value,
                                  name_index=arr_tickers, frequency=Frequency.DAILY, timeserie=TypeStrategy_strat.strat_data)
          
    Backtester_backtest = Backtester(config=Config_configuration, strat_data=pl.convert.from_pandas(TypeStrategy_strat.strat_data),
                                     timeserie=pl.convert.from_pandas(df), compo=dic_bloom, return_mat=df_return.dropna(), reshuffle=10)

    df_back = Backtester_backtest.compute_levels()

    # Loop on each element of backtester object to format json
    dict_quotes = []
    for quote in df_back:
        dict_quote = {'ts': quote.ts.isoformat(), 'close': quote.close}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_obj = json.dumps(dict_quotes)
    print(json_obj)

def json_dd(str_fields, str_tickers, date_start, date_end, str_strategie):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
    else :
        return "La stratégie n'est pas définie"

    # Retrieval of data obtained from Bloomberg
    df_data = pd.read_csv('./Python/data/generic.csv', index_col=0).dropna(axis=1)
    list_index = df_data.columns
    df_data.index = pd.to_datetime(df_data.index)
    df_data.sort_index(inplace=True)

    # Strategy definition
    TypeStrategy_strat = Strategies(TypeStrategy_strategie)
    TypeStrategy_strat.data_strategies(df_data.copy(), 5, 25)

    # Keep only data we are interested in
    df_data.reset_index(inplace=True)
    df_data.rename(columns={"index": 'Date'}, inplace=True)
    df = df_data[df_data.Date >= TypeStrategy_strat.strat_data['Date'][0]]

    # Composition of syntethic index
    df_compo = pd.DataFrame(np.zeros(
        (TypeStrategy_strat.strat_data.shape[0], 2)), columns=['Date', 'Compo'])
    df_compo['Date'] = TypeStrategy_strat.strat_data['Date']
    df_compo['Compo'] = [TypeStrategy_strat.strat_data.columns[1:].to_list()
                         for _ in range(len(df_compo))]

    dic_bloom = {(df_compo['Date'][0], 'CAC Index'): df_compo['Compo'][0][:40],
                 (df_compo['Date'][5], 'CAC Index'): df_compo['Compo'][5][10:50],
                 (df_compo['Date'][10], 'CAC Index'): df_compo['Compo'][50][:40]}

    # Calculation percentage return rate
    df_return = df_data.copy()
    df_return.iloc[:, 1:] = df_return.iloc[:, 1:].pct_change()

    Config_configuration = Config(universe=list_index, start_ts=TypeStrategy_strat.strat_data.Date.iloc[0],
                                  end_ts=TypeStrategy_strat.strat_data.Date.iloc[-1], strategy_code=TypeStrategy_strategie.value,
                                  name_index=arr_tickers, frequency=Frequency.DAILY, timeserie=TypeStrategy_strat.strat_data)
          
    Backtester_backtest = Backtester(config=Config_configuration, strat_data=pl.convert.from_pandas(TypeStrategy_strat.strat_data),
                                     timeserie=pl.convert.from_pandas(df), compo=dic_bloom, return_mat=df_return.dropna(), reshuffle=10)

    df_backtester = pd.DataFrame(Backtester_backtest.compute_levels())
    int_max = df_backtester['close'].cummax()
    df_dd = pd.DataFrame(df_backtester['close'] / int_max - 1.0)

    # Loop on each element of backtester object to format json
    dict_quotes = []
    for int_element in range(len(df_dd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'drawdown': df_dd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_obj = json.dumps(dict_quotes)
    print(json_obj)

def json_mdd(str_fields, str_tickers, date_start, date_end, str_strategie):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
    else :
        return "La stratégie n'est pas définie"

    # Retrieval of data obtained from Bloomberg
    df_data = pd.read_csv('./Python/data/generic.csv', index_col=0).dropna(axis=1)
    list_index = df_data.columns
    df_data.index = pd.to_datetime(df_data.index)
    df_data.sort_index(inplace=True)

    # Strategy definition
    TypeStrategy_strat = Strategies(TypeStrategy_strategie)
    TypeStrategy_strat.data_strategies(df_data.copy(), 5, 25)

    # Keep only data we are interested in
    df_data.reset_index(inplace=True)
    df_data.rename(columns={"index": 'Date'}, inplace=True)
    df = df_data[df_data.Date >= TypeStrategy_strat.strat_data['Date'][0]]

    # Composition of syntethic index
    df_compo = pd.DataFrame(np.zeros(
        (TypeStrategy_strat.strat_data.shape[0], 2)), columns=['Date', 'Compo'])
    df_compo['Date'] = TypeStrategy_strat.strat_data['Date']
    df_compo['Compo'] = [TypeStrategy_strat.strat_data.columns[1:].to_list()
                         for _ in range(len(df_compo))]

    dic_bloom = {(df_compo['Date'][0], 'CAC Index'): df_compo['Compo'][0][:40],
                 (df_compo['Date'][5], 'CAC Index'): df_compo['Compo'][5][10:50],
                 (df_compo['Date'][10], 'CAC Index'): df_compo['Compo'][50][:40]}

    # Calculation percentage return rate
    df_return = df_data.copy()
    df_return.iloc[:, 1:] = df_return.iloc[:, 1:].pct_change()

    Config_configuration = Config(universe=list_index, start_ts=TypeStrategy_strat.strat_data.Date.iloc[0],
                                  end_ts=TypeStrategy_strat.strat_data.Date.iloc[-1], strategy_code=TypeStrategy_strategie.value,
                                  name_index=arr_tickers, frequency=Frequency.DAILY, timeserie=TypeStrategy_strat.strat_data)
          
    Backtester_backtest = Backtester(config=Config_configuration, strat_data=pl.convert.from_pandas(TypeStrategy_strat.strat_data),
                                     timeserie=pl.convert.from_pandas(df), compo=dic_bloom, return_mat=df_return.dropna(), reshuffle=10)

    df_backtester = pd.DataFrame(Backtester_backtest.compute_levels())
    int_max = df_backtester['close'].cummax()
    serie_dd = df_backtester['close'] / int_max - 1.0
    df_mdd = pd.DataFrame(serie_dd.cummin())

    # Loop on each element of backtester object to format json
    dict_quotes = []
    for int_element in range(len(df_mdd)):
        dict_quote = {'ts': df_backtester.iloc[int_element].ts.isoformat(), 'mdd': df_mdd.iloc[int_element]['close']}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_obj = json.dumps(dict_quotes)
    print(json_obj)

def list_values(str_fields, str_tickers, date_start, date_end, str_strategie):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
    else :
        return "La stratégie n'est pas définie"

    # Retrieval of data obtained from Bloomberg
    df_data = pd.read_csv('./Python/data/generic.csv', index_col=0).dropna(axis=1)
    list_index = df_data.columns
    df_data.index = pd.to_datetime(df_data.index)
    df_data.sort_index(inplace=True)

    # Strategy definition
    TypeStrategy_strat = Strategies(TypeStrategy_strategie)
    TypeStrategy_strat.data_strategies(df_data.copy(), 5, 25)

    # Keep only data we are interested in
    df_data.reset_index(inplace=True)
    df_data.rename(columns={"index": 'Date'}, inplace=True)
    df = df_data[df_data.Date >= TypeStrategy_strat.strat_data['Date'][0]]

    # Composition of syntethic index
    df_compo = pd.DataFrame(np.zeros(
        (TypeStrategy_strat.strat_data.shape[0], 2)), columns=['Date', 'Compo'])
    df_compo['Date'] = TypeStrategy_strat.strat_data['Date']
    df_compo['Compo'] = [TypeStrategy_strat.strat_data.columns[1:].to_list()
                         for _ in range(len(df_compo))]

    dic_bloom = {(df_compo['Date'][0], 'CAC Index'): df_compo['Compo'][0][:40],
                 (df_compo['Date'][5], 'CAC Index'): df_compo['Compo'][5][10:50],
                 (df_compo['Date'][10], 'CAC Index'): df_compo['Compo'][50][:40]}

    # Calculation percentage return rate
    df_return = df_data.copy()
    df_return.iloc[:, 1:] = df_return.iloc[:, 1:].pct_change()

    Config_configuration = Config(universe=list_index, start_ts=TypeStrategy_strat.strat_data.Date.iloc[0],
                                  end_ts=TypeStrategy_strat.strat_data.Date.iloc[-1], strategy_code=TypeStrategy_strategie.value,
                                  name_index=arr_tickers, frequency=Frequency.DAILY, timeserie=TypeStrategy_strat.strat_data)
          
    Backtester_backtest = Backtester(config=Config_configuration, strat_data=pl.convert.from_pandas(TypeStrategy_strat.strat_data),
                                     timeserie=pl.convert.from_pandas(df), compo=dic_bloom, return_mat=df_return.dropna(), reshuffle=10)

    df_backtester = pd.DataFrame(Backtester_backtest.compute_levels())

    # Historical VaR
    ret = df_backtester.close.pct_change().dropna().sort_values().reset_index(drop=True)
    float_VaR = round(ret[int((1-0.95) * ret.shape[0])-1], 2)

    float_hitratio = round(Backtester_backtest.hit_dict['hit'] / Backtester_backtest.hit_dict['total_position_taken'], 2)
    float_meanhits = round(Backtester_backtest.hit_dict['mean_ret_from_hits'], 5)
    float_meanmisses = round(Backtester_backtest.hit_dict['mean_ret_from_misses'], 5)
    
    # Loop on each element of backtester object to format json
    arr_values = [float_VaR, float_hitratio, float_meanhits, float_meanmisses]
    arr_names = ["float_VaR", "float_hitratio", "float_meanhits", "float_meanmisses"]

    dict_quotes = []
    for int_element in range(len(arr_values)):
        dict_quote = {'variable': arr_names[int_element], 'value': arr_values[int_element]}
        dict_quotes.append(dict_quote)

    # Creation of json object
    json_obj = json.dumps(dict_quotes)
    print(json_obj)

def json_tuw(str_fields, str_tickers, date_start, date_end, str_strategie):
    arr_tickers = str_tickers.split(", ")  
    arr_fields = str_fields.split(", ") 
    # Strategy type definition
    if str_strategie == "momentum":
        TypeStrategy_strategie = TypeStrategy.momentum
    elif str_strategie == "mc":
        TypeStrategy_strategie = TypeStrategy.mc
    elif str_strategie == "btm":
        TypeStrategy_strategie = TypeStrategy.btm
    else :
        return "La stratégie n'est pas définie"

    # Retrieval of data obtained from Bloomberg
    df_data = pd.read_csv('./Python/data/generic.csv', index_col=0).dropna(axis=1)
    list_index = df_data.columns
    df_data.index = pd.to_datetime(df_data.index)
    df_data.sort_index(inplace=True)

    # Strategy definition
    TypeStrategy_strat = Strategies(TypeStrategy_strategie)
    TypeStrategy_strat.data_strategies(df_data.copy(), 5, 25)

    # Keep only data we are interested in
    df_data.reset_index(inplace=True)
    df_data.rename(columns={"index": 'Date'}, inplace=True)
    df = df_data[df_data.Date >= TypeStrategy_strat.strat_data['Date'][0]]

    # Composition of syntethic index
    df_compo = pd.DataFrame(np.zeros(
        (TypeStrategy_strat.strat_data.shape[0], 2)), columns=['Date', 'Compo'])
    df_compo['Date'] = TypeStrategy_strat.strat_data['Date']
    df_compo['Compo'] = [TypeStrategy_strat.strat_data.columns[1:].to_list()
                         for _ in range(len(df_compo))]

    dic_bloom = {(df_compo['Date'][0], 'CAC Index'): df_compo['Compo'][0][:40],
                 (df_compo['Date'][5], 'CAC Index'): df_compo['Compo'][5][10:50],
                 (df_compo['Date'][10], 'CAC Index'): df_compo['Compo'][50][:40]}

    # Calculation percentage return rate
    df_return = df_data.copy()
    df_return.iloc[:, 1:] = df_return.iloc[:, 1:].pct_change()

    Config_configuration = Config(universe=list_index, start_ts=TypeStrategy_strat.strat_data.Date.iloc[0],
                                  end_ts=TypeStrategy_strat.strat_data.Date.iloc[-1], strategy_code=TypeStrategy_strategie.value,
                                  name_index=arr_tickers, frequency=Frequency.DAILY, timeserie=TypeStrategy_strat.strat_data)
          
    Backtester_backtest = Backtester(config=Config_configuration, strat_data=pl.convert.from_pandas(TypeStrategy_strat.strat_data),
                                     timeserie=pl.convert.from_pandas(df), compo=dic_bloom, return_mat=df_return.dropna(), reshuffle=10)
    print(Backtester_backtest.tuw)

def return_values(str_fields, str_tickers, date_start, date_end, str_strategie, str_options):
    return (json_close(str_fields, str_tickers, date_start, date_end, str_strategie), 
          json_dd(str_fields, str_tickers, date_start, date_end, str_strategie), 
          json_mdd(str_fields, str_tickers, date_start, date_end, str_strategie),
          list_values(str_fields, str_tickers, date_start, date_end, str_strategie))


if __name__ == '__main__':
    return_values(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[7])