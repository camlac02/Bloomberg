import numpy as np
import pandas as pd


class Simulate:
    def __init__(self, returns):
        self.ret = returns
        self.ret[np.isnan(self.ret)] = 0
        self.arr_correlated_returns_sim = None
        self.dfGenericData = None

    def simulation_return(self):
        # mean and return of true data
        int_mu, int_std = np.nanmean(self.ret, axis=0), np.nanstd(self.ret, axis=0)
        # correlation between assets

        arr_corr = np.corrcoef(self.ret, rowvar=False)
        arr_cholesky = np.linalg.cholesky(arr_corr)

        # uncorrelated variables
        arr_z_stats = np.random.normal(size=(self.ret.shape[0], self.ret.shape[1]))

        # correlated them using cholesky decomposition
        arr_correlated_z_stats = (arr_cholesky @ arr_z_stats.T).T

        # retrieve correlated returns
        arr_correlated_returns_sim = int_mu + arr_correlated_z_stats * int_std
        # correlated_returns_sim[0, :] = np.zeros((self.ret.shape[1]))
        arr_correlated_returns_sim = np.vstack([np.zeros(arr_correlated_returns_sim.shape[1]), arr_correlated_returns_sim])
        return arr_correlated_returns_sim

    def recover_dataset(self, S0):
        self.arr_correlated_returns_sim = self.simulation_return()
        self.dfGenericData = S0.T * np.cumprod(1 + self.arr_correlated_returns_sim, axis=0)

    def compute_sim_dataset(self, S0, idx, col):
        self.recover_dataset(S0)
        self.dfGenericData = pd.DataFrame(self.dfGenericData)
        self.dfGenericData.columns = col
        self.dfGenericData.index = idx

    @staticmethod
    def cholesky_decomposition(corr):
        """
        Some instability makes it works only for small matrix
        Allow to find the Triangular Lower matrix used in the decompostion of a matrix:
        A = LL^(-1)
        :return: L
        """
        if np.sum(np.linalg.eigvals(corr) < 0) > 0:
            raise ValueError(
                "Matrice has to be semi definite. Here is the eigenvalues found: "
                + str(np.linalg.eigvals(corr))
            )

        L = np.zeros((len(corr), len(corr)))

        for j in range(len(corr)):

            L[j, j] = np.sqrt(
                corr[j, j] - np.sum([L[j, k] ** 2 for k in range(0, j)])
            )

            for i in range(j + 1, len(corr)):

                L[i, j] = (
                    corr[i, j] - np.sum([L[i, j - 1] * L[j, k] for k in range(0, j)])
                ) / L[j, j]

        return L


if __name__ == '__main__':
    data = pd.read_csv('data/data_blp1.csv', index_col=0).dropna(axis=1)
    ret = data.pct_change().dropna().to_numpy()
    sim = Simulate(ret)
    sim.compute_sim_dataset(data.iloc[0, :].to_numpy().reshape(-1, 1), idx=data.index[1:], col=data.columns)