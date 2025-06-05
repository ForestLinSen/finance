import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

from portfolio import Portfolio


def plot_var_cvar(data, alpha=0.95):
    log_ret = np.log(data / data.shift(1)).dropna()
    portfolio_ret = log_ret.mean(axis=1)
    var = np.quantile(portfolio_ret, 1 - alpha)
    cvar = portfolio_ret[portfolio_ret <= var].mean()

    plt.figure(figsize=(10, 6))
    plt.hist(portfolio_ret, bins=50, alpha=0.7, label="Returns")
    plt.axvline(var, color="r", linestyle="--", label=f"VaR {alpha*100:.0f}%")
    plt.axvline(cvar, color="k", linestyle="-.", label="CVaR")
    plt.text(
        var,
        plt.ylim()[1] * 0.9,
        f"VaR: {var:.2%}",
        ha="right",
        va="center",
        rotation=90,
        bbox=dict(fc="white", ec="black", lw=0.5),
    )
    plt.text(
        cvar,
        plt.ylim()[1] * 0.8,
        f"CVaR: {cvar:.2%}",
        ha="right",
        va="center",
        rotation=90,
        bbox=dict(fc="white", ec="black", lw=0.5),
    )
    plt.legend()
    plt.title("Portfolio VaR & CVaR")
    plt.xlabel("Log Return")
    plt.ylabel("Frequency")
    plt.show()


def plot_capm(symbols, start, end, market_symbol="^GSPC"):
    market = yf.download(market_symbol, start=start, end=end)["Close"].pct_change().dropna()
    plt.figure(figsize=(6 * len(symbols), 4))
    for idx, sym in enumerate(symbols):
        asset = yf.download(sym, start=start, end=end)["Close"].pct_change().dropna()
        df = pd.concat([asset, market], axis=1).dropna()
        df.columns = ["asset", "market"]
        beta, alpha = np.polyfit(df["market"], df["asset"], 1)
        r_squared = np.corrcoef(df["market"], df["asset"])[0, 1] ** 2
        ax = plt.subplot(1, len(symbols), idx + 1)
        ax.scatter(df["market"], df["asset"], alpha=0.5)
        ax.plot(df["market"], beta * df["market"] + alpha, color="red")
        ax.set_xlabel("Market Returns")
        ax.set_ylabel(f"{sym} Returns")
        ax.set_title(f"{sym} Beta={beta:.2f}")
        ax.annotate(
            f"Alpha={alpha:.2%}\nR²={r_squared:.2f}",
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            va="top",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5),
        )
    plt.tight_layout()
    plt.show()


class FinanceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Finance Visualisations")

        ttk.Label(self.root, text="Tickers (comma separated):").pack(pady=2)
        self.ticker_entry = ttk.Entry(self.root, width=50)
        self.ticker_entry.pack()
        self.ticker_entry.insert(0, "AAPL, MSFT, NVDA, META")

        ttk.Label(self.root, text="Start Date (YYYY-MM-DD):").pack(pady=2)
        self.start_entry = ttk.Entry(self.root)
        self.start_entry.insert(0, "2019-01-01")
        self.start_entry.pack()

        ttk.Label(self.root, text="End Date (YYYY-MM-DD):").pack(pady=2)
        self.end_entry = ttk.Entry(self.root)
        self.end_entry.insert(0, "2025-06-01")
        self.end_entry.pack()

        ttk.Label(self.root, text="Visualisation Type:").pack(pady=2)
        self.option_var = tk.StringVar()
        self.option_var.set("Efficient Frontier")
        options = ["Efficient Frontier", "VaR & CVaR", "CAPM Beta"]
        ttk.OptionMenu(self.root, self.option_var, options[0], *options).pack()

        ttk.Button(self.root, text="Run", command=self.run_analysis).pack(pady=4)
        self.root.mainloop()

    def run_analysis(self):
        tickers = [t.strip() for t in self.ticker_entry.get().split(",") if t.strip()]
        if not tickers:
            messagebox.showerror("Error", "Please enter at least one ticker")
            return
        start = self.start_entry.get()
        end = self.end_entry.get()
        option = self.option_var.get()
        if option == "Efficient Frontier":
            portfolio = Portfolio(tickers, start, end, sample_num=1000)
            portfolio.draw()
        elif option == "VaR & CVaR":
            portfolio = Portfolio(tickers, start, end, sample_num=1000)
            plot_var_cvar(portfolio.data)
        elif option == "CAPM Beta":
            plot_capm(tickers, start, end)


if __name__ == "__main__":
    FinanceGUI()
