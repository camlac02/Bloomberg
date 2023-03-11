import numpy as np
import pandas as pd


class Simulate:
    def __init__(self, returns):
        self.ret = returns
        self.correlated_returns_sim = None
        self.generic_data = None

    def simulation_return(self):
        '''
        Travailler l'explication
        :return:
        '''
        # mean and return of true data
        ret_centered = self.ret.copy() - self.ret.mean(axis=0)

        mu, std = ret_centered.mean(axis=0), ret_centered.std(axis=0)
        # correlation between assets
        corr = np.corrcoef(ret_centered, rowvar=False)
        cholesky = np.linalg.cholesky(corr)

        # uncorrelated variables
        z_stats = np.random.normal(size=(ret_centered.shape[0], ret_centered.shape[1]))

        # correlated them using cholesky decomposition
        correlated_z_stats = (cholesky @ z_stats.T).T

        # retrieve correlated returns
        correlated_returns_sim = mu + correlated_z_stats * std
        correlated_returns_sim[0, :] = np.zeros((ret_centered.shape[1]))
        return correlated_returns_sim

    def recover_dataset(self, S0, nIter=3):
        self.correlated_returns_sim = np.mean([self.simulation_return() for i in range(nIter)], axis=0)
        self.generic_data = S0.T * np.cumprod(1 + self.correlated_returns_sim, axis=0)

    def compute_sim_dataset(self, S0, idx, col, nIter=3):
        self.recover_dataset(S0, nIter)
        self.generic_data = pd.DataFrame(self.generic_data)
        self.generic_data.columns = col
        self.generic_data.index = idx

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
    sim.generic_data.to_csv('data/generic.csv')
