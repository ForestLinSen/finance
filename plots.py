import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def plot_efficient_frontier(portfolio):
    # Generate hover text for each simulated portfolio
    hover_texts = []
    for i in range(portfolio.sample_num):
        weights = portfolio.all_weights[i, :]
        weights_desc = "<br>".join([f"{sym}: {w*100:.1f}%" for sym, w in zip(portfolio.data.columns, weights)])
        text = (
            f"<b>Simulated Portfolio</b><br>"
            f"Return: {portfolio.ret_arr[i]:.2%}<br>"
            f"Volatility: {portfolio.vol_arr[i]:.2%}<br>"
            f"Sharpe: {portfolio.sharpe_arr[i]:.2f}<br>"
            f"----------<br>"
            f"{weights_desc}"
        )
        hover_texts.append(text)

    fig = go.Figure()

    # Use Scattergl for better performance
    fig.add_trace(go.Scattergl(
        x=portfolio.vol_arr,
        y=portfolio.ret_arr,
        mode='markers',
        marker=dict(
            color=portfolio.sharpe_arr,
            showscale=True,
            colorscale='Inferno',
            size=5,
            colorbar=dict(title='Sharpe Ratio'),
        ),
        text=hover_texts,
        hoverinfo='text',
        name='Simulated Portfolios'
    ))

    # Efficient frontier line
    fig.add_trace(go.Scatter(
        x=portfolio.frontier_x,
        y=portfolio.frontier_y,
        mode='lines',
        line=dict(color='#732AC6', width=3, dash='dash'),
        name='Efficient Frontier'
    ))

    # Optimal portfolio point
    optimal_weights_desc = "<br>".join(
        [f"{sym}: {w*100:.1f}%" for sym, w in zip(portfolio.data.columns, portfolio.optimal_weights)]
    )
    optimal_hover_text = (
        f"<b>Optimal Portfolio</b><br>"
        f"Return: {portfolio.optimal_ret:.2%}<br>"
        f"Volatility: {portfolio.optimal_vol:.2%}<br>"
        f"Sharpe: {portfolio.get_ret_vol_sr(portfolio.optimal_weights)[2]:.2f}<br>"
        f"----------<br>"
        f"{optimal_weights_desc}"
    )
    fig.add_trace(go.Scatter(
        x=[portfolio.optimal_vol],
        y=[portfolio.optimal_ret],
        mode='markers',
        marker=dict(color='#3C136B', size=15, symbol='star', line=dict(width=1, color='black')),
        text=[optimal_hover_text],
        hoverinfo='text',
        name='Optimal Solution'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Volatility',
        yaxis_title='Return',
        xaxis=dict(tickformat=".1%", fixedrange=True),
        yaxis=dict(tickformat=".1%", fixedrange=True),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=600,
        margin=dict(b=100)  # Bottom margin for horizontal legend
    )
    return fig

def plot_var_cvar(data, alpha=0.95):
    log_ret = np.log(data / data.shift(1)).dropna()
    portfolio_ret = log_ret.mean(axis=1)
    var = np.quantile(portfolio_ret, 1 - alpha)
    cvar = portfolio_ret[portfolio_ret <= var].mean()

    fig = px.histogram(portfolio_ret, nbins=50, title='Portfolio VaR & CVaR')
    fig.add_vline(x=var, line_width=2, line_dash="dash", line_color="red", name=f'VaR {alpha*100:.0f}%')
    fig.add_vline(x=cvar, line_width=2, line_dash="dot", line_color="black", name='CVaR')
    
    fig.update_layout(
        xaxis_title='Log Return',
        yaxis_title='Frequency',
        legend_title="Metrics",
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )
    return fig

def plot_capm(data, market_data, symbols):
    market_returns = market_data.pct_change().dropna()
    
    num_symbols = len(symbols)
    fig = make_subplots(rows=1, cols=num_symbols, subplot_titles=symbols)

    for i, sym in enumerate(symbols):
        asset_returns = data[sym].pct_change().dropna()
        df = pd.concat([asset_returns, market_returns], axis=1).dropna()
        df.columns = ["asset", "market"]
        
        beta, alpha = np.polyfit(df["market"], df["asset"], 1)
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=df["market"], y=df["asset"], mode='markers',
            name=f'{sym} vs Market',
            marker=dict(opacity=0.5)
        ), row=1, col=i+1)
        
        # Regression line
        fig.add_trace(go.Scatter(
            x=df["market"], y=beta * df["market"] + alpha,
            mode='lines', line=dict(color='red'),
            name='CAPM Line'
        ), row=1, col=i+1)
        
        # Update subplot title correctly
        fig.layout.annotations[i].text = f"{sym} (Beta={beta:.2f})"
        
        fig.update_xaxes(title_text="Market Returns", row=1, col=i+1, fixedrange=True)
        fig.update_yaxes(title_text=f"{sym} Returns", row=1, col=i+1, fixedrange=True)

    fig.update_layout(showlegend=False, height=400, width=300 * num_symbols)
    return fig

def plot_correlation_matrix(data):
    corr = data.pct_change().corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title='Asset Correlation Matrix')
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig

def plot_portfolio_performance(portfolio):
    # Cumulative returns for the optimal portfolio
    optimal_portfolio_daily_returns = portfolio.log_ret.dot(portfolio.optimal_weights)
    optimal_cumulative = (1 + optimal_portfolio_daily_returns).cumprod()
    
    # Cumulative returns for individual assets
    individual_asset_cumulative_returns = (1 + portfolio.log_ret).cumprod()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=optimal_cumulative.index,
        y=optimal_cumulative,
        mode='lines',
        name='Optimal Portfolio',
        line=dict(width=4)
    ))

    for asset in individual_asset_cumulative_returns.columns:
        fig.add_trace(go.Scatter(
            x=individual_asset_cumulative_returns.index,
            y=individual_asset_cumulative_returns[asset],
            mode='lines',
            name=asset,
            line=dict(width=1, dash='dot'),
            opacity=0.8
        ))

    fig.update_layout(
        title='Portfolio Performance vs. Individual Assets',
        xaxis_title='Date',
        yaxis_title='Cumulative Growth',
        legend_title="Assets",
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )
    return fig
