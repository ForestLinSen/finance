import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import warnings
from matplotlib import style

warnings.filterwarnings("ignore")


class Portfolio:
    def __init__(self, data_symbol, start_date, end_date, line=True, sample_num=10000):
        self.data_symbol = data_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.create_stock_data(self.data_symbol)
        self.length = len(self.data.columns)
        self.sample_num = sample_num
        self.calculate(line=line)

    def create_stock_data(self, data_symbol):
        data = pd.DataFrame()
        for symbol in data_symbol:
            try:
                symbol_data = yf.download(symbol, start=self.start_date, end=self.end_date)
                str_index = [str(idx)[:10] for idx in symbol_data.index]
                symbol_data.index = str_index
                data = pd.concat([data, symbol_data["Close"]], axis=1)
            except Exception as e:
                print(f"股票代码有误：{symbol}，错误：{e} / Error with stock symbol {symbol}: {e}")
        data.columns = data_symbol
        data = data.dropna()
        return data

    def calculate(self, line):
        self.all_weights = np.zeros((self.sample_num, self.length))
        self.ret_arr = np.zeros(self.sample_num)
        self.vol_arr = np.zeros(self.sample_num)
        self.sharpe_arr = np.zeros(self.sample_num)
        self.log_ret = np.log(self.data / self.data.shift(1))

        for x in range(self.sample_num):
            self.weights = np.random.dirichlet(np.ones(self.length), size=1)[0]
            self.all_weights[x, :] = self.weights
            self.ret_arr[x] = np.sum(self.log_ret.mean() * self.weights * 252)
            self.vol_arr[x] = np.sqrt(np.dot(self.weights.T, np.dot(self.log_ret.cov() * 252, self.weights)))
            self.sharpe_arr[x] = self.ret_arr[x] / self.vol_arr[x]

        cons = ({"type": "eq", "fun": self.check_sum},)
        bounds = ((0, 1),) * self.length
        init_guess = np.full(self.length, 1 / self.length)
        result_optimal = minimize(self.neg_sharpe, init_guess, method="SLSQP", bounds=bounds, constraints=cons)
        self.optimal_weights = result_optimal.x
        self.optimal_ret, self.optimal_vol, _ = self.get_ret_vol_sr(self.optimal_weights)

        self.frontier_x = []
        min_vol_ret = self.ret_arr[np.argmin(self.vol_arr)]
        self.frontier_y = np.linspace(min_vol_ret, self.ret_arr.max(), 100)
        for target_return in self.frontier_y:
            cons = (
                {"type": "eq", "fun": self.check_sum},
                {"type": "eq", "fun": lambda w, tr=target_return: self.get_ret_vol_sr(w)[0] - tr},
            )
            result = minimize(self.minimize_volatility, init_guess, method="SLSQP", bounds=bounds, constraints=cons)
            self.frontier_x.append(result.fun)

    def draw(self, line=True):
        plt.figure(figsize=(15, 8))
        sc = plt.scatter(self.vol_arr, self.ret_arr, c=self.sharpe_arr, cmap="inferno", s=10, alpha=0.7)
        plt.colorbar(sc, label="Sharpe Ratio")
        plt.xlabel("Volatility")
        plt.ylabel("Return")
        plt.xticks(np.arange(0, 0.5, 0.1))
        plt.yticks(np.arange(-0.1, 0.6, 0.2))

        if line:
            plt.plot(self.frontier_x, self.frontier_y, "--", color="#732AC6", linewidth=3)

        plt.scatter(self.optimal_vol, self.optimal_ret, c="#3C136B", marker="o", s=120, edgecolors="black", label="Optimal Solution")

        weights_desc = "\n".join([f"{sym}: {w*100:.1f}%" for sym, w in zip(self.data.columns, self.optimal_weights)])
        annotation_text = (
            f"From {self.start_date} to {self.end_date}:\n"
            f"----------\n"
            f"Return: {self.optimal_ret:.2%}\n"
            f"Volatility: {self.optimal_vol:.2%}\n"
            f"Sharpe: {self.get_ret_vol_sr(self.optimal_weights)[2]:.2f}\n"
            f"----------\n"
            f"{weights_desc}"
        )

        plt.annotate(
            annotation_text,
            xy=(self.optimal_vol, self.optimal_ret),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5),
            arrowprops=dict(arrowstyle="->", lw=0.5),
        )

        plt.legend()
        plt.title("Efficient Frontier")
        plt.tight_layout()
        plt.show()

    def report(self):
        best_idx = self.sharpe_arr.argmax()
        best_weights = self.all_weights[best_idx]
        print(f"The selected time range is: {self.start_date} - {self.end_date}")
        print("Optimal simulated portfolio:")
        for sym, w in zip(self.data.columns, best_weights):
            print(f"  {sym}: {w*100:.2f}%")
        best_ret, best_vol, best_sr = self.get_ret_vol_sr(best_weights)
        print(f"Expected Annual Return: {best_ret*100:.2f}%, Volatility: {best_vol*100:.2f}%, Sharpe: {best_sr:.2f}")

    def get_ret_vol_sr(self, weights):
        weights = np.asarray(weights)
        ret = np.sum(self.log_ret.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov() * 252, weights)))
        sr = ret / vol
        return ret, vol, sr

    def neg_sharpe(self, weights):
        return -self.get_ret_vol_sr(weights)[2]

    def check_sum(self, weights):
        return np.sum(weights) - 1

    def minimize_volatility(self, weights):
        return self.get_ret_vol_sr(weights)[1]


if __name__ == "__main__":
    start_date = "2019-01-01"
    end_date = "2024-04-01"
    data_array = ["600519.SS", "0700.HK", "BABA", "AAPL", "MSFT", "TSLA"]
    portfolio = Portfolio(data_array, start_date, end_date, sample_num=1000)
    portfolio.report()
    portfolio.draw()
