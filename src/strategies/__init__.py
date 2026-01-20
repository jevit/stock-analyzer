"""Strategies module - Signal detection."""
from src.strategies.base import StrategyResult
from src.strategies.trend_pullback import TrendPullbackStrategy
from src.strategies.breakout import BreakoutStrategy
from src.strategies.mean_reversion import MeanReversionStrategy

__all__ = [
    "StrategyResult",
    "TrendPullbackStrategy",
    "BreakoutStrategy",
    "MeanReversionStrategy",
]
