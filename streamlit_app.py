import streamlit as st
from datetime import date
import yfinance as yf

from portfolio import Portfolio
from plots import (
    plot_efficient_frontier,
    plot_var_cvar,
    plot_capm,
    plot_correlation_matrix,
    plot_portfolio_performance,
)

st.set_page_config(page_title="Finance Visualisations", layout="wide")

@st.cache_data
def download_data(tickers, start, end):
    """Downloads and caches financial data from Yahoo Finance."""
    data = yf.download(tickers, start=start, end=end)["Close"]
    return data.dropna()

def init_session_state():
    """Initializes session state variables."""
    if 'plots' not in st.session_state:
        st.session_state.plots = []

init_session_state()

st.title("Finance Visualisations")

st.sidebar.header("User Input")
tickers_input = st.sidebar.text_input(
    "Tickers (comma-separated)", "AAPL,MSFT,NVDA,META"
)
tickers = sorted([ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()])

start_date = st.sidebar.date_input("Start Date", date(2019, 1, 1))
end_date = st.sidebar.date_input("End Date", date(2025, 6, 1))

risk_free_rate = st.sidebar.slider(
    "Risk-Free Rate (%)", 0.0, 5.0, 2.0, 0.1
)

sample_num = st.sidebar.slider(
    "Number of Samples", 1000, 20000, 10000, 1000
)

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    [
        "Efficient Frontier",
        "Portfolio Performance",
        "VaR & CVaR",
        "CAPM Beta",
        "Correlation Matrix",
    ],
)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("Run Analysis", use_container_width=True):
        if not tickers:
            st.warning("Please enter at least one ticker.")
        else:
            with st.spinner('Performing analysis...'):
                try:
                    data = download_data(tuple(tickers), start_date, end_date)
                    if data.empty:
                        st.error("Could not download valid data for the selected tickers and date range.")
                    else:
                        plot_info = {"type": analysis_type, "tickers": ", ".join(tickers)}
                        
                        if analysis_type in ["Efficient Frontier", "Portfolio Performance"]:
                            portfolio = Portfolio(data, str(start_date), str(end_date), risk_free_rate / 100, sample_num=sample_num)
                            if analysis_type == "Efficient Frontier":
                                plot_info["fig"] = plot_efficient_frontier(portfolio)
                            elif analysis_type == "Portfolio Performance":
                                plot_info["fig"] = plot_portfolio_performance(portfolio)
                        
                        elif analysis_type == "VaR & CVaR":
                            plot_info["fig"] = plot_var_cvar(data)
                        elif analysis_type == "CAPM Beta":
                            market_data = download_data(("^GSPC",), start_date, end_date)
                            plot_info["fig"] = plot_capm(data, market_data, tickers)
                        elif analysis_type == "Correlation Matrix":
                            plot_info["fig"] = plot_correlation_matrix(data)
                        
                        st.session_state.plots.append(plot_info)
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with col2:
    if st.button("Clear All Plots", use_container_width=True):
        st.session_state.plots = []

# Display all generated plots in reverse order
if st.session_state.plots:
    for plot in reversed(st.session_state.plots):
        st.subheader(f"{plot['type']} for {plot['tickers']}")
        st.plotly_chart(plot['fig'], use_container_width=True)
else:
    st.info("Click 'Run Analysis' to generate visuals.")

st.sidebar.info(
    "This app provides portfolio analytics based on live Yahoo Finance data."
)
