"""
Breakout Strategy.

Detects price breakouts above recent highs with volume confirmation.
Conditions:
- Close > highest high over 55 days
- Volume > 1.5x average 20-day volume
- ATR% > 1% (avoid flat stocks)
"""
import pandas as pd
from loguru import logger

from config.settings import get_settings
from src.strategies.base import BaseStrategy, StrategyResult


class BreakoutStrategy(BaseStrategy):
    """Breakout strategy implementation."""

    name = "Breakout"
    description = "Price breakout above 55-day high with volume surge"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Evaluate Breakout conditions.

        Args:
            df: DataFrame with indicators

        Returns:
            StrategyResult with signal and scoring
        """
        result = StrategyResult(strategy_name=self.name)

        if not self._check_data_validity(df):
            result.warnings.append("Insufficient data for analysis")
            return result

        # Get latest and previous values
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        close = latest["Close"]
        high_55d = latest.get("High_55d", df["High"].rolling(55).max().iloc[-1])
        prev_high_55d = prev.get("High_55d", df["High"].rolling(55).max().iloc[-2]) if len(df) > 1 else high_55d
        atr = latest["ATR"]
        atr_pct = latest["ATR_pct"]
        volume_ratio = latest["Volume_ratio"]
        sma200 = latest["SMA200"]

        # Track conditions
        conditions = {}
        score_components = {}

        # Condition 1: Close > 55-day high (breakout)
        # We need to check if TODAY we broke above the PREVIOUS high
        # (not the current high which includes today)
        lookback = self.settings.breakout_lookback_days
        if len(df) > lookback:
            prior_high = df["High"].iloc[-(lookback+1):-1].max()
        else:
            prior_high = high_55d

        conditions["breakout"] = close > prior_high
        if conditions["breakout"]:
            breakout_pct = ((close - prior_high) / prior_high) * 100
            result.reasons.append(f"Cassure du plus haut {lookback}j (+{breakout_pct:.1f}%)")
            # Score based on strength of breakout
            if breakout_pct >= 3:
                score_components["breakout"] = 35
            elif breakout_pct >= 1:
                score_components["breakout"] = 30
            else:
                score_components["breakout"] = 25
        else:
            result.warnings.append(f"Pas de cassure (close {close:.2f} vs high {prior_high:.2f})")
            score_components["breakout"] = 0

        # Condition 2: Volume surge
        min_volume_ratio = self.settings.breakout_volume_multiplier
        conditions["volume_surge"] = volume_ratio >= min_volume_ratio
        if volume_ratio >= 2.0:
            result.reasons.append(f"Volume très élevé ({volume_ratio:.1f}x moyenne)")
            score_components["volume"] = 35
        elif volume_ratio >= min_volume_ratio:
            result.reasons.append(f"Volume élevé ({volume_ratio:.1f}x moyenne)")
            score_components["volume"] = 25
        elif volume_ratio >= 1.0:
            result.warnings.append(f"Volume moyen ({volume_ratio:.1f}x) - confirmation faible")
            score_components["volume"] = 10
        else:
            result.warnings.append(f"Volume faible ({volume_ratio:.1f}x) - breakout suspect")
            score_components["volume"] = 0

        # Condition 3: Sufficient volatility (ATR% > 1%)
        min_atr_pct = self.settings.breakout_min_atr_pct
        conditions["volatility"] = atr_pct >= min_atr_pct
        if atr_pct >= 2.0:
            result.reasons.append(f"Bonne volatilité (ATR {atr_pct:.1f}%)")
            score_components["volatility"] = 20
        elif atr_pct >= min_atr_pct:
            result.reasons.append(f"Volatilité suffisante (ATR {atr_pct:.1f}%)")
            score_components["volatility"] = 15
        else:
            result.warnings.append(f"Action trop plate (ATR {atr_pct:.1f}%)")
            score_components["volatility"] = 0

        # Bonus: Trend context
        trend_bonus = 0
        if close > sma200:
            result.reasons.append("Tendance de fond haussière (prix > SMA200)")
            trend_bonus = 10
        else:
            result.warnings.append("Breakout contre tendance (prix < SMA200)")

        # Calculate total score
        total_score = sum(score_components.values()) + trend_bonus

        # Signal detected if main conditions are met
        signal_detected = (
            conditions["breakout"] and
            conditions["volume_surge"] and
            conditions["volatility"]
        )

        # Calculate technical levels (wider for breakouts)
        entry = close
        invalidation = close - (atr * 2.5)  # Wider stop for breakouts
        target = close + (atr * 3.0)  # Higher target for momentum
        rr_ratio = self._calculate_risk_reward(entry, invalidation, target)

        # Build result
        result.signal_detected = signal_detected
        result.score = min(100, total_score)
        result.entry_level = round(entry, 2)
        result.invalidation_level = round(invalidation, 2)
        result.target_level = round(target, 2)
        result.risk_reward_ratio = rr_ratio

        result.metrics = {
            "close": close,
            "high_55d": prior_high,
            "atr": atr,
            "atr_pct": atr_pct,
            "volume_ratio": volume_ratio,
            "sma200": sma200,
            "conditions": conditions,
            "score_components": score_components,
            "trend_bonus": trend_bonus,
        }

        logger.debug(f"Breakout: signal={signal_detected}, score={total_score}")

        return result
