import random
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
from typing import List
import pandas as pd
from warnings import warn
from time import time
from functools import reduce
import polars as pl

warn('Running this module requires the package: polars 0.15.14')


class Frequency(Enum):
    HOURLY = "Hourly"
    MONTHLY = "Monthly"
    DAILY = "Daily"


@dataclass
class Config:
    universe: List[str]
    start_ts: datetime
    end_ts: datetime
    strategy_code: str
    name_index: str
    frequency: Frequency
    basis: int = 100
    timeserie: np.array = None

    def __post_init__(self):
        if self.start_ts >= self.end_ts:
            raise ValueError("self.start_ts must be before self.end_ts")
        if len(self.universe) == 0:
            raise ValueError("self.universe should contains at least one element")

    @property
    def timedelta(self):
        if self.frequency == Frequency.HOURLY:
            return timedelta(hours=1)
        if self.frequency == Frequency.DAILY:
            return timedelta(days=1)

    def calendar(self, timeserie) -> List[datetime]:
        # renvoyer une liste de date comprise entre start_ts et end_ts.
        # create calendar of date
        if timeserie is None:
            timedelta_ = self.timedelta
            tmp = self.start_ts
            calendar_ = []
            while tmp <= self.end_ts:
                calendar_.append(tmp)
                tmp += timedelta_
            return calendar_
        else:
            return timeserie['Date']


@dataclass
class Quote:
    ts: datetime = None
    close: float = None


@dataclass
class Weight:
    product_code: str = None
    underlying_code: str = None
    ts: datetime = None
    value: float = None


class Backtester:
    """
    4/ Record every backtest conducted on a dataset so that the probability of backtest
    overfitting may be estimated on the final selected result (see Bailey, Borwein,
    Lopez de Prado, and Zhu [2017a] and Chapter 14), and the Sharpe ratio may ´
    be properly deflated by the number of trials carried out (Bailey and Lopez de ´
    Prado [2014b]).
    5/ Simulate scenarios rather than history (Chapter 12). A standard backtest is a
    historical simulation, which can be easily overfit. History is just the random
    path that was realized, and it could have been entirely different. Your strategy
    should be profitable under a wide range of scenarios, not just the anecdotal
    historical path. It is harder to overfit the outcome of thousands of “what if”
    scenarios.
    Chapter 14 for statistics
    """

    def __init__(self, config: Config, strat_data, compo, timeserie=None, reshuffle=1):
        self._config = config
        self._calendar = config.calendar(timeserie[::reshuffle])  # create calendar
        self._universe = config.universe
        self._timedelta = config.timedelta

        self._quote_by_pk = dict()
        self._weight_by_pk = dict()
        self._level_by_ts = dict()
        self.reshuffle = reshuffle
        self.compo = compo  # compo of indexes through time

        self.compute_positions(pos=strat_data[::reshuffle], index_name=config.name_index)
        if self._config.start_ts != timeserie['Date'][0]:
            raise ValueError(
                "starts_ts and the start date of the raw data have to be the same"
            )
        self._generate_quotes(timeserie)

        # for hit ratio
        self.hit_dict = {'hit': 0, 'hit_long': 0, 'hit_short': 0, 'total_position_taken': 0,
                         'total_position_taken_long': 0, 'total_position_taken_short': 0,
                         'mean_ret_from_misses': list(), 'mean_ret_from_hits': list()}
        self.tuw = None  # time under water
        self.dd = None  # drawdown

    def _generate_quotes(self, quote_data):
        """
        quote_data: data from which we create the quote
        """
        for ts in self._calendar:
            for underlying_code in self._universe:
                if quote_data is None:
                    self._quote_by_pk[(underlying_code, ts - self._timedelta)] = Quote(
                        close=100 * (1 + random.random() / 100), ts=ts - self._timedelta
                    )
                else:
                    self._quote_by_pk[(underlying_code, ts - self._timedelta)] = Quote(
                        close=quote_data.filter((pl.col('Date') == ts)).select([str(underlying_code)]),
                        ts=ts - self._timedelta,
                    )

    def _compute_weight(self, ts: datetime, nb_stock):
        """
        nb_stock: we only use the columns 'sum_h' of the dataframe which is the number of stock which we hold
                at time ts ==> allow us to compute the weight
        Function which compute the weight depending on the strategy
        """
        nb_stock_to_hold = nb_stock.filter((pl.col('Date') == ts)).select(['sum_h'])
        # same weight attributed for stock we go long on
        w = nb_stock_to_hold.apply(lambda x: np.divide(1, x)) if nb_stock_to_hold.to_pandas().values[0][0] != 0 else 0

        for underlying_code in self._universe:
            # weight_giver: we multiply the weight given at the underlying by 0 (if not buy) or 1 (if buy)
            weight_given = (
                    self.position.filter((pl.col('Date') == ts)).select([str(underlying_code)]) * w
            )
            self._weight_by_pk[
                (self._config.strategy_code, underlying_code, ts)
            ] = Weight(
                product_code=self._config.strategy_code,
                underlying_code=underlying_code,
                ts=ts,
                value=weight_given,
            )

    def _compute_perf(self, ts: datetime, prev_ts: datetime) -> float:
        """
        Function which compute the perf of our strategy
        """
        perf_ = 0.0
        for underlying_code in self._universe:
            posi = self.position.filter((pl.col('Date') == ts)).select([str(underlying_code)])
            key = (self._config.strategy_code, underlying_code, prev_ts)

            weight = self._weight_by_pk.get(
                key
            )
            if weight is not None:
                value = weight.value * posi
                current_quote = self._quote_by_pk.get(
                    (underlying_code, ts - self._timedelta)
                )
                key = (underlying_code, prev_ts - self._timedelta)
                # start = 2 because current quote is taken at ts - _timedelta
                previous_quote = self._quote_by_pk.get(
                    key
                )

                if current_quote is not None and previous_quote is not None:
                    rdt = (current_quote.close / previous_quote.close - 1)
                    perf_ += value * rdt

                    # update hit statistics
                    value_int = value.to_numpy()[0][0].copy()
                    if value_int != 0:
                        self.update_hit(rdt, value_int)
                else:
                    raise ValueError(
                        f"missing quote for {underlying_code} at {prev_ts - self._timedelta} "
                        f"or {ts - self._timedelta}"
                    )
        return perf_

    def compute_levels(self) -> List[Quote]:
        """
        Compute the level of our portfolio at each timestamp
        :return: level of ptf
        """
        # compute the number of stock which will have a weight different from 0
        nb_stock_to_hold_per_period = self.position.with_column(pl.fold(0, lambda x, y: x + y, pl.all().exclude('Date'))
                                                                .alias('sum_h'))
        for ts in self._calendar:
            self._compute_weight(ts, nb_stock_to_hold_per_period)
            if ts == self._config.start_ts:
                quote = Quote(close=self._config.basis, ts=ts - self._timedelta)
                self._level_by_ts[ts - self._timedelta] = quote
            else:
                perf = self._compute_perf(ts, prev_ts=prev_ts)
                close = self._level_by_ts.get(prev_ts - self._timedelta).close * (
                        1 + perf
                ).to_pandas().values[0][0]
                quote = Quote(close=close, ts=ts)
                self._level_by_ts[ts - self._timedelta] = quote
            prev_ts = ts

        self.update_hit(end=True)
        ret = list(self._level_by_ts.values())
        self.TuW(pd.DataFrame(ret.copy()))
        return ret

    def compute_positions(self, pos, index_name, q=0.25):
        """
        :param pos: strategy data reshuffled
        :param index_name: CAC Index for exemple
        :param q: part of long / short
        :return: full df of positions
        """
        pos = pos.to_pandas()
        # select all the stock which have been in the index
        my_list = list(self.compo.values())
        unique_list = list(set(reduce(lambda x,y : x+y, my_list)))
        #unique_list = list(set(flat_list))

        self.position = pd.DataFrame(np.zeros((pos.shape[0], len(unique_list) + 1)), columns=['Date'] + unique_list)
        self.position.Date = pos['Date']
        datetime_next_loop = [key[0] for key in self.compo.keys()] # list datetime recompute compo
        for ts in pos['Date']:
            # compo at time ts
            ts_for_dict, datetime_next_loop = self.find_closest_datetime(ts, datetime_next_loop) # date at which we take the compo
            compo_ts = self.compo[(ts_for_dict, index_name[0])] # list compo at date ts
            # position we take in this univers

            # stop there
            pos_ts = self.compute_position_ts(compo_ts, pos, ts, q=q)
            self.position.loc[self.position.Date == ts, compo_ts] = pos_ts
        self.position = pl.convert.from_pandas(self.position)

    @staticmethod
    def find_closest_datetime(timestamp, datetimes):
        """
        Find the closest datetime that comes before the given timestamp in a list of datetimes.
        Basically find the ts at which the last compo of index has been take out bloomberg
        """
        closest = None
        old = None
        datetime_next_loop = datetimes.copy()
        for dt in datetimes:
            if dt <= timestamp:
                closest = dt
                if old is not None:
                    datetime_next_loop.remove(old)
                old = dt
                continue
        return closest, datetime_next_loop

    @staticmethod
    def compute_position_ts(compo, pos, ts, q=0.25):
        """
        :param compo: compo of index
        :param pos: strategy data reshuffled
        :param ts: current time
        :param q: part of long / short
        :return: position for 1 timestamp
        """
        nb_position = int((len(compo) - 1) * q)
        pos_ts = pos[pos.Date == ts]
        long = np.sort(pos_ts.iloc[:, 1:], axis=1)[:, -nb_position - 1]
        short = np.sort(pos_ts.iloc[:, 1:], axis=1)[:, nb_position]

        # define the weight to 2 when values are >= to the quantile at 75%
        weights_long = pos_ts.iloc[:, 1:].where(pos_ts.iloc[:, 1:].values < long.reshape(-1, 1), 2)
        weights_long = weights_long.where(weights_long.values == 2)

        # define the weight to -1 when values are < to the quantile at 25%
        weights_short = pos_ts.iloc[:, 1:].where(pos_ts.iloc[:, 1:].values > short.reshape(-1, 1), -1)
        weights_short = weights_short.where(weights_short.values == -1)

        dfs = [weights_long, weights_short]
        return reduce(lambda dfA, dfB: dfB.combine_first(dfA), dfs).fillna(0)

    def update_hit(self, returns=None, val=None, end=False):
        '''
        :param returns: curr_quote / prev_quote - 1
        :param val: weight
        :param end: bool
        :return: compute hit scores of the strategy
        '''
        if end:
            for key in self.hit_dict.keys():
                x = self.hit_dict[key]
                if isinstance(x, list):
                    self.hit_dict[key] = np.mean(x)
            return
        returns = returns.to_numpy()[0][0].copy()
        if val > 0:
            id = returns > 0
            self.hit_dict['hit_long'] += id
            self.hit_dict['total_position_taken_long'] += 1

            # moyenne des returns lors d'une pos longue
            self.hit_dict['mean_ret_from_hits'].append(returns * id)
            self.hit_dict['mean_ret_from_misses'].append(returns * (1-id))
        elif val < 0:
            id = returns < 0
            self.hit_dict['hit_short'] += id
            self.hit_dict['total_position_taken_short'] += 1

            self.hit_dict['mean_ret_from_hits'].append(-returns * id)
            self.hit_dict['mean_ret_from_misses'].append(-returns * (1 - id))

        if np.sign(val) == np.sign(returns):
            self.hit_dict['hit'] += 1

        self.hit_dict['total_position_taken'] += 1

    def TuW(self, pnl: pd.DataFrame):
        """
        :param pnl: series of pnl
        : compute Time under water and drawdowns using high-watermarks
        """
        pnl.set_index(pnl.ts, inplace=True)
        pnl.drop('ts', inplace=True, axis=1)
        pnl['hwm'] = pnl['close'].expanding().max()  # max from the beginning of the quotations
        df1 = pnl.groupby('hwm').min().reset_index()
        df1.index = pnl['hwm'].drop_duplicates(keep='first').index
        df1.columns = ['hwm', 'min']
        df1 = df1[df1['hwm'] > df1['min']]
        self.dd = 1 - df1['min'] / df1['hwm']
        tuw = (df1.index[1:] - df1.index[:-1])
        self.tuw = pd.Series(tuw, index=df1.index[:-1])