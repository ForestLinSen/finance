import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


class Portfolio:
  def __init__(self, data_symbol, line=True,sample_num = 10000):
    self.data_symbol = data_symbol
    self.data = self.create_stock_data(self.data_symbol)
    self.length = len(self.data.columns)
    self.sample_num = sample_num
    self.calculate(line=line)

  # 用雅虎财经API创建Data
  def create_stock_data(self, data_symbol):
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
      except:
        print("请检查股票代码拼写是否有误！")
    data.columns = data_symbol
    data = data.dropna()
    return data

  def calculate(self, line):
    # 初始化参数
    self.all_weights = np.zeros((self.sample_num, len(self.data.columns)))
    self.ret_arr = np.zeros(self.sample_num)
    self.vol_arr = np.zeros(self.sample_num)
    self.sharpe_arr = np.zeros(self.sample_num)
    self.log_ret = np.log(self.data/self.data.shift(1))

    for x in range(self.sample_num):
      # 随机给不同资产赋予权重
      self.weights = np.array(np.random.random(self.length))
      self.weights = self.weights/np.sum(self.weights)
      self.all_weights[x,:] = self.weights

      # 计算期望收益
      # 252是美股每年的交易天数
      self.ret_arr[x] = np.sum( (self.log_ret.mean() * self.weights * 252))
      # 计算期望风险
      self.vol_arr[x] = np.sqrt(np.dot(self.weights.T, np.dot(self.log_ret.cov()*252, self.weights)))

      # 计算夏普比率
      self.sharpe_arr[x] = self.ret_arr[x]/ self.vol_arr[x]

    self.frontier_x = []
    self.frontier_y = np.linspace(-0.1, 0.5, 100)

    for possible_return in self.frontier_y:
      cons = ({'type':'eq','fun': self.check_sum}, {'type':'eq','fun':lambda w : self.get_ret_vol_sr(w)[0]-possible_return})
      init_guess = np.ones(self.length) / (self.length)
      bounds = ((0,1),)*(self.length)
      self.result = minimize(self.minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
      self.frontier_x.append(self.result['fun'])

  def draw(self, line=True):
    plt.figure(figsize=(15,8))
    plt.scatter(self.vol_arr, self.ret_arr, c=self.sharpe_arr, cmap='viridis', s=10)
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.xticks(np.arange(0, 0.5, step=0.1))
    plt.yticks(np.arange(-0.1, 0.6, step=0.2))
    if(line):
      plt.plot(self.frontier_x, self.frontier_y, 'r--', linewidth=3)
    plt.show()

  def report(self):
    self.optim_number = self.sharpe_arr.argmax()
    self.optim_weights = self.all_weights[self.optim_number]
    print("基于所选风险资产的模拟最佳组合: ")
    for i in range(self.length):
      print("股票代码：{}, 比例：{:.2f}%".format(self.data.columns[i], self.optim_weights[i]*100))
    self.best_results_arr = self.get_ret_vol_sr( self.optim_weights)
    print("期望年化收益: {:.2f}%, 风险: {:.2f}%".format(self.best_results_arr[0]*100, self.best_results_arr[1]*100, self.best_results_arr[2]))


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


####根据需要调整下面的参数####
if __name__ == "__main__":
    # 数据起始日期
    start_date = "2019-01-01"
    end_date = "2022-10-01"
    # 选择需要哪些资产的数据
    data_array = ["600519.SS", "0700.HK","BABA", "AAPL", "MSFT", "TSLA"]
    # data_array = ["BABA", "AAPL", "MSFT", "TSLA"]

    portfolio = Portfolio(data_array, sample_num=1000)
    portfolio.report()
    portfolio.draw()
