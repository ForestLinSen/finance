[EN](README.md) | [中文](README_CN.md)

## About
Finance Visualisations is a lightweight desktop app that lets you explore core portfolio analytics—Efficient Frontier, VaR & CVaR, and CAPM beta—straight from live Yahoo Finance data with a single click, and I'll keep updating it with additional visual insights in the future.

The efficient frontier calculation part of this code is primarily based on the article by Fábio Neves, where you can find detailed explanations: [Plotting Markowitz Efficient Frontier with Python](https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5). I have extended this by integrating the Yahoo Finance API, allowing direct calculations using stock codes. Weights are generated using the Dirichlet distribution rather than the default uniform distribution, ensuring that the sum of weights equals 1.


## Install Dependencies
In the project folder, install the dependencies using the following command:

```
pip install -r requirements.txt
```

## How to Use (GUI update)

1. You can also launch a simple GUI tool that integrates multiple
   visualisations:

```
python gui_tool.py
```

## A Few Notes

- Modify the `start_date` and `end_date` accordingly. Be aware that some companies, such as Bilibili which was listed in 2018, may not have accurate data if your start date is before their listing date.

- Change or add to the `data_array` with asset codes. There is no limit on the number of assets. This uses the Yahoo Finance API; search for company codes with "company name + Yahoo Finance", e.g., "600519.SS" for Maotai, "AAPL" for Apple, and "0700.HK" for Tencent.

- The calculation results are for informational use only. Please be aware that investing involves risks, and decisions should be made with careful consideration.

![Graph](screenshots/figure1.jpeg)
![Graph](screenshots/figure2.jpeg)
![Graph](screenshots/figure3.jpeg)
![Graph](screenshots/figure4.jpeg)