[EN](README.md) / [中文](README_CN.md)

## 关于
代码计算部分主要参考了Fábio Neves的文章，其中包含详细的解释：[Plotting Markowitz Efficient Frontier with Python](https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5)。我在此基础上加入了雅虎财经API的调用，可直接使用股票代码进行计算。在权重生成方面，我使用了狄利克雷分布而非默认的均匀分布，确保权重之和为1。


## 安装依赖
在项目文件夹中，使用以下命令安装依赖：

```
pip install -r requirements.txt
```

## 使用方法
1. 在`portfolio.py`代码文件中设置以下参数：
   - `start_date` - 数据起始日期
   - `end_date` - 数据结束日期
   - `data_array` - 股票代码数组

2. 在命令行中，执行以下命令运行代码：

```
python portfolio.py
```

## 一些说明

- 修改`start_date`和`end_date`。请注意，部分公司如Bilibili于2018年上市，如果开始日期早于上市日期，可能会导致数据不准确。

- 更改或添加`data_array`中的资产代号。此处使用雅虎财经API，你可以通过“公司名+雅虎财经”搜索对应的公司代号，如茅台是“600519.SS”，苹果是“AAPL”，腾讯是“0700.HK”。

- 如果计算时间过长，可尝试减少`sample_num`的值。

- 计算结果仅供参考。投资有风险，入市需谨慎。

![图表](screenshots/graph.png)