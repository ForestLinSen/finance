[EN](README.md) / [中文](README_CN.md)

## 关于
Finance Visualisations 是一个轻量级的Web应用程序，让你可以直接从Yahoo Finance的实时数据中探索核心的投资组合分析，包括有效前沿、VaR和CVaR、CAPM贝塔系数、相关矩阵和投资组合表现。

此代码的有效前沿计算部分主要基于Fábio Neves的文章，你可以在其中找到详细的解释：[用Python绘制马科维茨有效前沿](https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5)。我通过集成Yahoo Finance API对此进行了扩展，允许直接使用股票代码进行计算。权重是使用狄利克雷分布而不是默认的均匀分布生成的，以确保权重总和为1。

## 安装依赖
在项目文件夹中，使用以下命令安装依赖：

```
pip install -r requirements.txt
```

## 如何使用（Web应用程序）

1. 启动Streamlit Web应用程序：

```
streamlit run streamlit_app.py
```

2. 使用侧边栏输入股票代码，选择日期，设置无风险利率，并选择分析类型。

## 一些说明

- 请注意，某些公司（如2018年上市的Bilibili）如果您的开始日期早于其上市日期，可能没有准确的数据。
- 本程序使用雅虎财经API；请使用“公司名称 + Yahoo Finance”搜索公司代码，例如，茅台为“600519.SS”，苹果为“AAPL”，腾讯为“0700.HK”。
- 计算结果仅供参考。请注意，投资涉及风险，应谨慎决策。

![Graph](screenshots/figure1.jpeg)
![Graph](screenshots/figure2.jpeg)
