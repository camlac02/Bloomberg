import numpy as np
import pandas as pd
import sys
import subprocess
from enum import Enum
from datetime import datetime
# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                       'datetime'])
import datetime


class TypeStrategy(Enum):
    momentum = 'momentum'
    btm = 'btm'
    mc = 'mc'


class Strategies:
    def __init__(self, strategy=TypeStrategy.mc):
        self.strategy = strategy
        self.strat_data = None

    def momentum(self, data, lag1, lag2):
        self.strat_data = pd.DataFrame(np.zeros((data.shape[0] - lag2, data.shape[1])), columns=data.columns)
        for t in range(lag2, data.shape[0]):
            self.strat_data.loc[t - lag2] = data.iloc[t - lag1] / data.iloc[t - lag2] - 1
        self.strat_data.index = data.index[lag2:]

    def data_strategies(self, data, lag1=None, lag2=None, other_data=None):
        """

        :param data: returns
        :param lag1: for mom
        :param lag2: for mom
        :param other_data: for btc
        :return:
        """
        if self.strategy == TypeStrategy.momentum.value:
            if lag1 is None or lag2 is None:
                raise ValueError('lag1 or lag2 have to be set')
            self.momentum(data, lag1, lag2)
        elif self.strategy == TypeStrategy.mc.value:
            self.strat_data = data

        elif self.strategy == TypeStrategy.btm.value:
            if other_data is None:
                raise ValueError('other_data have to be define as mkt_cap')
            other_data.reset_index(inplace=True, drop=True)
            self.strat_data = data.div(other_data)  # book / mkt_cap
        else:
            raise ValueError('strategy name is not adapted')

        #self.strat_data.reset_index(inplace=True)
        #self.strat_data.rename(columns={"index": 'Date'}, inplace=True)

