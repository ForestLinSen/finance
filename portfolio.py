import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings

warnings.filterwarnings("ignore")

class Portfolio:
    def __init__(self, data, start_date, end_date, risk_free_rate=0.02, sample_num=10000):
        if data.empty or len(data.columns) < 1:
            raise ValueError("Input data is empty or invalid.")
            
        self.data = data
        self.data_symbol = data.columns.tolist()
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        self.sample_num = sample_num
        self.length = len(self.data.columns)
        self.calculate()

    def calculate(self):
        self.all_weights = np.zeros((self.sample_num, self.length))
        self.ret_arr = np.zeros(self.sample_num)
        self.vol_arr = np.zeros(self.sample_num)
        self.sharpe_arr = np.zeros(self.sample_num)
        self.log_ret = np.log(self.data / self.data.shift(1))

        for x in range(self.sample_num):
            weights = np.random.dirichlet(np.ones(self.length), size=1)[0]
            self.all_weights[x, :] = weights
            ret, vol, sr = self.get_ret_vol_sr(weights)
            self.ret_arr[x] = ret
            self.vol_arr[x] = vol
            self.sharpe_arr[x] = sr

        cons = ({"type": "eq", "fun": self.check_sum},)
        bounds = ((0, 1),) * self.length
        init_guess = np.full(self.length, 1 / self.length)
        
        result_optimal = minimize(self.neg_sharpe, init_guess, method="SLSQP", bounds=bounds, constraints=cons)
        self.optimal_weights = result_optimal.x
        self.optimal_ret, self.optimal_vol, _ = self.get_ret_vol_sr(self.optimal_weights)

        self.frontier_x = []
        min_vol_ret = self.ret_arr[np.argmin(self.vol_arr)]
        
        if self.optimal_ret < min_vol_ret:
             min_vol_ret = self.optimal_ret * 0.9
        
        self.frontier_y = np.linspace(min_vol_ret, self.ret_arr.max(), 100)
        
        for target_return in self.frontier_y:
            cons_frontier = (
                {"type": "eq", "fun": self.check_sum},
                {"type": "eq", "fun": lambda w, tr=target_return: self.get_ret_vol_sr(w)[0] - tr},
            )
            result = minimize(self.minimize_volatility, init_guess, method="SLSQP", bounds=bounds, constraints=cons_frontier)
            if result.success:
                self.frontier_x.append(result.fun)
            else:
                self.frontier_x.append(np.nan)
        
        self.frontier_y = np.array(self.frontier_y)
        self.frontier_x = np.array(self.frontier_x)
        valid_front = ~np.isnan(self.frontier_x)
        self.frontier_x = self.frontier_x[valid_front]
        self.frontier_y = self.frontier_y[valid_front]

    def get_ret_vol_sr(self, weights):
        weights = np.asarray(weights)
        ret = np.sum(self.log_ret.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov() * 252, weights)))
        sr = (ret - self.risk_free_rate) / vol if vol != 0 else 0
        return ret, vol, sr

    def neg_sharpe(self, weights):
        return -self.get_ret_vol_sr(weights)[2]

    def check_sum(self, weights):
        return np.sum(weights) - 1

    def minimize_volatility(self, weights):
        return self.get_ret_vol_sr(weights)[1]
