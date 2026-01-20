"""
Base strategy class and common types.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd


@dataclass
class StrategyResult:
    """Result of a strategy evaluation."""

    # Signal detection
    signal_detected: bool = False
    strategy_name: str = ""

    # Scoring (0-100)
    score: int = 0

    # Explanations
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Technical levels (indicative only)
    entry_level: Optional[float] = None
    invalidation_level: Optional[float] = None
    target_level: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # Additional metrics
    metrics: dict = field(default_factory=dict)

    def __str__(self) -> str:
        if not self.signal_detected:
            return f"{self.strategy_name}: No signal"
        return f"{self.strategy_name}: Score {self.score}/100 - {', '.join(self.reasons[:2])}"


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    name: str = "BaseStrategy"
    description: str = "Base strategy class"

    @abstractmethod
    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Evaluate the strategy on price data.

        Args:
            df: DataFrame with OHLCV data and calculated indicators

        Returns:
            StrategyResult with signal detection and scoring
        """
        pass

    def analyze(self, df: pd.DataFrame) -> StrategyResult:
        """
        Alias for evaluate() - for backward compatibility.

        Args:
            df: DataFrame with OHLCV data and calculated indicators

        Returns:
            StrategyResult with signal detection and scoring
        """
        return self.evaluate(df)

    def _calculate_levels(
        self,
        close: float,
        atr: float,
        atr_multiplier: float = 2.0
    ) -> tuple[float, float, float]:
        """
        Calculate indicative technical levels.

        Args:
            close: Current close price
            atr: Average True Range
            atr_multiplier: Multiplier for ATR (default 2.0)

        Returns:
            Tuple of (entry, invalidation, target) levels
        """
        entry = close
        invalidation = close - (atr * atr_multiplier)
        target = close + (atr * atr_multiplier)

        return entry, invalidation, target

    def _calculate_risk_reward(
        self,
        entry: float,
        invalidation: float,
        target: float
    ) -> float:
        """
        Calculate risk/reward ratio.

        Args:
            entry: Entry price level
            invalidation: Stop loss level
            target: Target price level

        Returns:
            Risk/reward ratio (higher is better)
        """
        risk = abs(entry - invalidation)
        reward = abs(target - entry)

        if risk == 0:
            return 0.0

        return round(reward / risk, 2)

    def _check_data_validity(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has enough data for analysis."""
        if df is None or df.empty:
            return False

        # Need at least 200 days for SMA200
        if len(df) < 200:
            return False

        # Check for required indicator columns
        required = ["Close", "SMA50", "SMA200", "RSI", "ATR"]
        return all(col in df.columns for col in required)
