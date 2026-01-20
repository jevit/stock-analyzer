"""
Chart components using Plotly.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List


def create_price_chart(
    df: pd.DataFrame,
    ticker: str,
    show_sma: bool = True,
    show_bb: bool = True,
    show_volume: bool = True,
    signal_dates: Optional[List[pd.Timestamp]] = None,
    days: int = 180
) -> go.Figure:
    """
    Create a comprehensive price chart with indicators.

    Args:
        df: DataFrame with OHLCV and indicators
        ticker: Ticker symbol for title
        show_sma: Show SMAs
        show_bb: Show Bollinger Bands
        show_volume: Show volume subplot
        signal_dates: Dates to mark with vertical lines
        days: Number of days to display

    Returns:
        Plotly Figure
    """
    # Limit to recent data
    df = df.tail(days).copy()

    # Create subplots
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Prix",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1,
        col=1,
    )

    # SMAs
    if show_sma:
        if "SMA20" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["SMA20"],
                    name="SMA20",
                    line=dict(color="#2196f3", width=1),
                ),
                row=1,
                col=1,
            )
        if "SMA50" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["SMA50"],
                    name="SMA50",
                    line=dict(color="#ff9800", width=1.5),
                ),
                row=1,
                col=1,
            )
        if "SMA200" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["SMA200"],
                    name="SMA200",
                    line=dict(color="#9c27b0", width=2),
                ),
                row=1,
                col=1,
            )

    # Bollinger Bands
    if show_bb and "BB_upper" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_upper"],
                name="BB Upper",
                line=dict(color="rgba(128, 128, 128, 0.5)", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_lower"],
                name="BB Lower",
                line=dict(color="rgba(128, 128, 128, 0.5)", width=1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(128, 128, 128, 0.1)",
            ),
            row=1,
            col=1,
        )

    # Volume bars
    if show_volume and "Volume" in df.columns:
        colors = [
            "#26a69a" if c >= o else "#ef5350"
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2,
            col=1,
        )

        # Volume average line
        if "Volume_avg20" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["Volume_avg20"],
                    name="Vol Avg 20",
                    line=dict(color="#ff9800", width=1),
                ),
                row=2,
                col=1,
            )

    # Mark signal dates
    if signal_dates:
        for date in signal_dates:
            if date in df.index:
                fig.add_vline(
                    x=date,
                    line_width=2,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Signal",
                )

    # Layout
    fig.update_layout(
        title=f"{ticker} - Analyse Technique",
        xaxis_rangeslider_visible=False,
        height=600 if show_volume else 450,
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    fig.update_yaxes(title_text="Prix", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_indicator_chart(df: pd.DataFrame, days: int = 180) -> go.Figure:
    """
    Create a chart with RSI and ATR indicators.

    Args:
        df: DataFrame with indicators
        days: Number of days to display

    Returns:
        Plotly Figure
    """
    df = df.tail(days).copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.5, 0.5],
        subplot_titles=("RSI (14)", "ATR % (Volatilité)"),
    )

    # RSI
    if "RSI" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["RSI"],
                name="RSI",
                line=dict(color="#2196f3", width=1.5),
            ),
            row=1,
            col=1,
        )

        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=1, col=1)

        # Shade overbought/oversold
        fig.add_hrect(
            y0=70, y1=100, fillcolor="red", opacity=0.1, row=1, col=1
        )
        fig.add_hrect(
            y0=0, y1=30, fillcolor="green", opacity=0.1, row=1, col=1
        )

    # ATR %
    if "ATR_pct" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["ATR_pct"],
                name="ATR %",
                line=dict(color="#ff9800", width=1.5),
                fill="tozeroy",
                fillcolor="rgba(255, 152, 0, 0.2)",
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        height=400,
        template="plotly_dark",
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
    )

    fig.update_yaxes(range=[0, 100], row=1, col=1)
    fig.update_yaxes(title_text="ATR %", row=2, col=1)

    return fig


def create_mini_chart(df: pd.DataFrame, days: int = 60) -> go.Figure:
    """
    Create a minimal sparkline-style chart.

    Args:
        df: DataFrame with OHLCV
        days: Number of days

    Returns:
        Plotly Figure
    """
    df = df.tail(days).copy()

    # Determine color based on trend
    start_price = df["Close"].iloc[0]
    end_price = df["Close"].iloc[-1]
    color = "#26a69a" if end_price >= start_price else "#ef5350"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line=dict(color=color, width=1.5),
            fill="tozeroy",
            fillcolor=f"rgba{tuple(list(bytes.fromhex(color[1:])) + [0.2])}",
        )
    )

    fig.update_layout(
        height=80,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        template="plotly_dark",
    )

    return fig
