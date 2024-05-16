import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import warnings
from matplotlib import style

warnings.filterwarnings("ignore")


class Portfolio:
  def __init__(self, data_symbol, line=True,sample_num = 10000):
    self.data_symbol = data_symbol
    self.data = self.create_stock_data(self.data_symbol)
    self.length = len(self.data.columns)
    self.sample_num = sample_num
    self.calculate(line=line)

  def create_stock_data(self, data_symbol):
    """使用雅虎财经API创建股票数据 / Create stock data using the Yahoo Finance API."""
    data = pd.DataFrame()
    for symbol in data_symbol:
      try:
        symbol_data = yf.download(symbol, start=start_date, end=end_date)
        
        str_index = []
        for index in symbol_data.index:
            new_index = str(index)[:10]
            str_index.append(new_index)
        symbol_data.index = str_index
        data = pd.concat([data, symbol_data['Close']], axis=1)
      except Exception as e:
          print(f"股票代码有误：{symbol}，错误：{e} / Error with stock symbol {symbol}: {e}")
    data.columns = data_symbol
    data = data.dropna()
    return data

  def calculate(self, line):
      """计算投资组合统计数据 / Calculate portfolio statistics."""
      self.all_weights = np.zeros((self.sample_num, len(self.data.columns)))
      self.ret_arr = np.zeros(self.sample_num)
      self.vol_arr = np.zeros(self.sample_num)
      self.sharpe_arr = np.zeros(self.sample_num)
      self.log_ret = np.log(self.data/self.data.shift(1))

      for x in range(self.sample_num):
          # 随机给不同资产赋予权重 / Randomly assign weights to different assets
          self.weights = np.random.dirichlet(np.ones(self.length), size=1)[0]
          self.all_weights[x, :] = self.weights

          # 计算期望收益 / Calculate expected return
          # 252是美股每年的交易天数 / 252 is the number of trading days in a year
          self.ret_arr[x] = np.sum( (self.log_ret.mean() * self.weights * 252))
          # 计算期望风险 / Calculate expected risk
          self.vol_arr[x] = np.sqrt(np.dot(self.weights.T, np.dot(self.log_ret.cov()*252, self.weights)))

          # 计算夏普比率 / Calculate Sharpe Ratio
          self.sharpe_arr[x] = self.ret_arr[x]/ self.vol_arr[x]

      # Find the optimal weights with the highest Sharpe ratio on the efficient frontier
      cons = ({'type': 'eq', 'fun': self.check_sum})
      bounds = ((0, 1),) * (self.length)
      init_guess = np.ones(self.length) / self.length

      result_optimal = minimize(self.neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
      self.optimal_weights = result_optimal.x
      self.optimal_ret, self.optimal_vol, _ = self.get_ret_vol_sr(self.optimal_weights)

      self.frontier_x = []
      min_vol_index = np.argmin(self.vol_arr)
      min_vol_ret = self.ret_arr[min_vol_index]
      self.frontier_y = np.linspace(min_vol_ret, self.ret_arr.max(), 100)

      for possible_return in self.frontier_y:
          cons = ({'type':'eq','fun': self.check_sum}, {'type':'eq','fun':lambda w : self.get_ret_vol_sr(w)[0]-possible_return})
          init_guess = np.ones(self.length) / (self.length)
          bounds = ((0,1),)*(self.length)
          self.result = minimize(self.minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
          self.frontier_x.append(self.result['fun'])



  def draw(self, line=True):
      # style.use('seaborn-bright')
      plt.figure(figsize=(15,8))
      plt.scatter(self.vol_arr, self.ret_arr, c=self.sharpe_arr, cmap='inferno', s=10, alpha=0.7)
      plt.colorbar(label='Sharpe Ratio')
      plt.xlabel('Volatility')
      plt.ylabel('Return')
      plt.xticks(np.arange(0, 0.5, step=0.1))
      plt.yticks(np.arange(-0.1, 0.6, step=0.2))
      if(line):
          plt.plot(self.frontier_x, self.frontier_y, color="#732AC6", linestyle='--',  linewidth=3)

      # Plot the red dot on the optimal position on the efficient frontier
      plt.scatter(self.optimal_vol, self.optimal_ret, c='#3C136B', marker='o', s=120, edgecolors='black', label='Optimal Solution')
      plt.legend()
      plt.show()


  def report(self):
    self.optim_number = self.sharpe_arr.argmax()
    self.optim_weights = self.all_weights[self.optim_number]
    print("所选择的时间范围为：{} - {} / The selected time range is: {} - {}".format(start_date, end_date, start_date, end_date))
    print("基于所选风险资产的模拟最佳组合: / The optimal portfolio simulated based on the selected risk assets:")
    for i in range(self.length):
        print("股票(Stock): {}, 权重(weight): {:.2f}%".format(self.data.columns[i], self.optim_weights[i]*100))
    self.best_results_arr = self.get_ret_vol_sr(self.optim_weights)
    print("期望年化收益(Expected Annual Return): {:.2f}%, 风险(Volatility): {:.2f}%".format(self.best_results_arr[0]*100, self.best_results_arr[1]*100, self.best_results_arr[2]))


  def get_ret_vol_sr(self, weights):
      weights = np.array(weights)
      ret = np.sum(self.log_ret.mean() * weights) * 252
      vol = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov()*252, weights)))
      sr = ret/vol
      return np.array([ret, vol, sr])

  def neg_sharpe(self, weights):
    return self.get_ret_vol_sr(weights)[2] * -1

  def check_sum(self, weights):
      #return 0 if sum of the weights is 1
      return np.sum(weights)-1

  def minimize_volatility(self, weights):
      return self.get_ret_vol_sr(weights)[1]


if __name__ == "__main__":
    # 数据起始日期 / Data start date
    start_date = "2019-01-01"
    end_date = "2024-04-01"
    # 选择需要哪些资产的数据 / Choose which assets to use
    data_array = ["600519.SS", "0700.HK","BABA", "AAPL", "MSFT", "TSLA"]
    # data_array = ["BABA", "AAPL", "MSFT", "TSLA"]

    portfolio = Portfolio(data_array, sample_num=1000)
    portfolio.report()
    portfolio.draw()
