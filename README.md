[EN](README.md) | [中文](README_CN.md)

## About

The calculation part of this code is primarily based on the article by Fábio Neves, where you can find detailed explanations: [Plotting Markowitz Efficient Frontier with Python](https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5). I have extended this by integrating the Yahoo Finance API, allowing direct calculations using stock codes. Weights are generated using the Dirichlet distribution rather than the default uniform distribution, ensuring that the sum of weights equals 1.


## Install Dependencies
In the project folder, install the dependencies using the following command:

```
pip install -r requirements.txt
```

## How to Use
1. In the code file `portfolio.py`, set the following parameters:
   - `start_date` - Data start date
   - `end_date` - Data end date
   - `data_array` - Array of stock codes

2. Run the code with the following command in the command line:

```
python portfolio.py
```

## A Few Notes

- Modify the `start_date` and `end_date` accordingly. Be aware that some companies, such as Bilibili which was listed in 2018, may not have accurate data if your start date is before their listing date.

- Change or add to the `data_array` with asset codes. There is no limit on the number of assets. This uses the Yahoo Finance API; search for company codes with "company name + Yahoo Finance", e.g., "Maotai 600519.SS", "Apple AAPL", and "Tencent 0700.HK".

- If calculations take too long, consider reducing the `sample_num` value.

- Calculation results are for reference only. Investing carries risks, and caution is advised when entering the market.

![Graph](screenshots/graph.png)