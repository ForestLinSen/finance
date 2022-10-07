## 关于
1. 代码主要参考Fábio Neves的文章，你可以在他的文章中找到一些细节性的解释：https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5
 
## 使用说明
1. 修改起始时间`start_date`和`end_date`。需要注意有些公司上市时间可能比较迟，例如B站是在2018年上市，如果你的开始时间是从2015年开始，那么结果可能会不准确。
2. 修改和添加`data_array`中的资产代号，数量没有限制，这里使用的是雅虎财经的API，你可以在搜索引擎中以「公司名+雅虎财经（Yahoo Finance）」搜索对应公司代号。例如茅台是「600519.SS」，苹果是「AAPL」，腾讯是「0700.HK」。
3. 如果运算时间过长，你可以尝试降低`sample_num`的数值。
4. 计算结果仅供参考。投资有风险，入市需谨慎。

![](screenshots/graph.png)

