"""Backtesting module - Test strategies on historical data."""
from src.backtest.engine import BacktestEngine
from src.backtest.trade import Trade
from src.backtest.results import BacktestResults, analyze_trades, analyze_by_strategy, create_equity_curve

__all__ = [
    "BacktestEngine",
    "Trade",
    "BacktestResults",
    "analyze_trades",
    "analyze_by_strategy",
    "create_equity_curve"
]
