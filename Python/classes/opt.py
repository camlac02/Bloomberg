import sys
import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import math


class OptimizeAllocation:
    def __init__(self, returns, type_strat_alloc, w=None, rf=0):
        self.type_strat_alloc = type_strat_alloc

        # return matrix of only the stock which I am long (short) in
        self.return_matrix = returns
        self.return_matrix.fillna(0, inplace=True)
        self.initial_weight = w if None else np.array([1/returns.shape[0] - 0.01]*returns.shape[0])
        self.rf = rf
        self.final_weight = None
        self.sharpe = None

    def max_sharpe(self):
        var_cov = self.variance_covariance_matrix()
        ret_matrix = self.return_matrix

        def neg_sharpe(w):
            w = np.array(w)
            return -(w @ np.mean(ret_matrix, 1) - self.rf) * (w.T @ var_cov @ w) ** (
                    -1 / 2
            )

        cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        # bounds = tuple((0,10) for x in range(0,ret.shape[0]))
        optimized_weight = np.array(
            minimize(
                neg_sharpe,
                self.initial_weight,
                method='SLSQP',
                constraints=cons,
                bounds=((0.001, 1.0) for asset in range(len(self.initial_weight)))
            ).x
        )
        sharpe_ratio = np.sqrt((
                               optimized_weight @ np.mean(self.return_matrix, 1) - self.rf
                       ) * (optimized_weight.T @ var_cov @ optimized_weight) ** (-1 / 2))

        self.final_weight = optimized_weight
        self.sharpe = sharpe_ratio

    def variance_covariance_matrix(self):
        return np.cov(self.return_matrix) * np.sqrt(252)

    def min_variance(self):
        var_cov = self.variance_covariance_matrix()

        def ptf_variance(w, var_covar):
            w = np.array(w)
            return np.sqrt(w.T @ var_covar @ w)

        cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

        optimized_weight = np.array(
            minimize(
                ptf_variance,
                self.initial_weight,
                method="SLSQP",
                constraints=cons,
                args=var_cov,
                bounds=((0.001, 1.0) for asset in range(len(self.initial_weight)))
            ).x
        )

        self.final_weight = optimized_weight

    def risk_parity(self):
        _risk_contributions_fct = lambda w, C: (w @ C) * w / (w @ C @ w.T)
        _deviations = lambda w, C, dev: np.sum(abs(_risk_contributions_fct(w, C) - dev), axis=1)

        cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        optimized_weight = np.array(
            minimize(
                _deviations,
                self.initial_weight,
                method="SLSQP",
                constraints=cons,
                args=(self.variance_covariance_matrix(), np.array([1/len(self.initial_weight)] * len(self.initial_weight)).reshape(1, -1)),
                options={'maxiter': 100}
            ).x
        )

        self.final_weight = optimized_weight


    def efficient_ptf(self, target_risk):
        ret_matrix = self.return_matrix
        var_covar = self.variance_covariance_matrix().copy()

        def mean_return(w):
            w = np.array(w)
            return -w @ np.mean(ret_matrix, 1)

        cons = (
            # constraint that the sum of weights equals 1
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            # constraint that the portfolio risk (as measured by its variance or covariance) equals the target risk
            {"type": "eq", "fun": lambda w: w.T @ var_covar @ w - target_risk},
        )

        optimized_weight = np.array(
            minimize(
                mean_return,
                self.initial_weight,
                method="SLSQP",
                constraints=cons,
                bounds=((0.001, 1.0) for asset in range(len(self.initial_weight)))
            ).x
        )
        print(optimized_weight @ np.mean(self.return_matrix, 1))
        self.final_weight = optimized_weight


if __name__ == '__main__':
    import yfinance as yf

    x = {'gold': yf.Ticker("AAPL").history(period="10y").Close.pct_change().to_numpy()[1:1350],
        'ibm': yf.Ticker("AMZN").history(period="10y").Close.pct_change().to_numpy()[1:1350],
         'sg': yf.Ticker("GLE.PA").history(period="10y").Close.pct_change().to_numpy()[1:1350],
         'google': yf.Ticker("GOOG").history(period="10y").Close.pct_change().to_numpy()[1:1350]}

    q = np.array(list(x.values()))[:, 0:1300]

    opt = OptimizeAllocation(returns=q, w=np.array([0.1, 0.4, 0.4,0.05]), type_strat_alloc='min')
    #opt.min_variance()
    print(opt.type_strat_alloc)
    print(opt.final_weight)

    opt = OptimizeAllocation(returns=q, w=np.array([0.1, 0.4, 0.4,0.1]), type_strat_alloc='sharpe')
    print(opt.type_strat_alloc)
    opt.max_sharpe()
    print(opt.final_weight)

    opt = OptimizeAllocation(returns=q, w=np.array([0.1, 0.4, 0.4, 0.1]), type_strat_alloc='riskparity')
    print(opt.type_strat_alloc)
    opt.risk_parity()
    print(opt.final_weight)