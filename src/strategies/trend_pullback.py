"""
Trend Pullback Strategy.

Detects pullbacks to moving averages in an established uptrend.
Conditions:
- Close > SMA200 (uptrend)
- Close near SMA50 (distance < 2%)
- RSI crossing above 50 (momentum confirmation)
- Volume above average (interest confirmation)
"""
import pandas as pd
from loguru import logger

from config.settings import get_settings
from src.strategies.base import BaseStrategy, StrategyResult


class TrendPullbackStrategy(BaseStrategy):
    """Trend Pullback strategy implementation."""

    name = "Trend Pullback"
    description = "Pullback to SMA50 in uptrend with RSI and volume confirmation"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Evaluate Trend Pullback conditions.

        Args:
            df: DataFrame with indicators

        Returns:
            StrategyResult with signal and scoring
        """
        result = StrategyResult(strategy_name=self.name)

        if not self._check_data_validity(df):
            result.warnings.append("Insufficient data for analysis")
            return result

        # Get latest values
        latest = df.iloc[-1]
        close = latest["Close"]
        sma50 = latest["SMA50"]
        sma200 = latest["SMA200"]
        rsi = latest["RSI"]
        atr = latest["ATR"]
        volume_ratio = latest["Volume_ratio"]
        dist_sma50 = abs(latest["Dist_SMA50_pct"])
        rsi_crossed_50 = latest.get("RSI_crossed_50_up", False)

        # Track individual conditions
        conditions = {}
        score_components = {}

        # Condition 1: Close > SMA200 (uptrend)
        conditions["uptrend"] = close > sma200
        if conditions["uptrend"]:
            result.reasons.append("Prix au-dessus SMA200 (tendance haussière)")
            score_components["uptrend"] = 25
        else:
            result.warnings.append("Prix sous SMA200 - pas de tendance haussière établie")
            score_components["uptrend"] = 0

        # Condition 2: Close near SMA50
        max_distance = self.settings.pullback_sma_distance_pct
        conditions["near_sma50"] = dist_sma50 <= max_distance
        if conditions["near_sma50"]:
            # Closer is better
            proximity_score = max(0, 25 - (dist_sma50 / max_distance) * 15)
            result.reasons.append(f"Prix proche SMA50 ({dist_sma50:.1f}% de distance)")
            score_components["near_sma50"] = int(proximity_score)
        else:
            result.warnings.append(f"Prix trop éloigné de SMA50 ({dist_sma50:.1f}%)")
            score_components["near_sma50"] = 0

        # Condition 3: RSI crossing above 50
        conditions["rsi_momentum"] = rsi_crossed_50 and rsi > 50
        if conditions["rsi_momentum"]:
            result.reasons.append(f"RSI a croisé 50 à la hausse ({rsi:.1f})")
            score_components["rsi_momentum"] = 25
        elif rsi > 50:
            result.reasons.append(f"RSI au-dessus de 50 ({rsi:.1f})")
            score_components["rsi_momentum"] = 15
        else:
            result.warnings.append(f"RSI sous 50 ({rsi:.1f}) - momentum faible")
            score_components["rsi_momentum"] = 0

        # Condition 4: Volume above average
        conditions["volume_confirm"] = volume_ratio > 1.0
        if volume_ratio >= 1.5:
            result.reasons.append(f"Volume fort ({volume_ratio:.1f}x moyenne)")
            score_components["volume"] = 25
        elif volume_ratio >= 1.0:
            result.reasons.append(f"Volume correct ({volume_ratio:.1f}x moyenne)")
            score_components["volume"] = 15
        else:
            result.warnings.append(f"Volume faible ({volume_ratio:.1f}x moyenne)")
            score_components["volume"] = 0

        # Calculate total score
        total_score = sum(score_components.values())

        # Signal is detected if all main conditions are met
        signal_detected = (
            conditions["uptrend"] and
            conditions["near_sma50"] and
            (conditions["rsi_momentum"] or rsi > 50) and
            conditions["volume_confirm"]
        )

        # Calculate technical levels
        entry, invalidation, target = self._calculate_levels(close, atr, 2.0)
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
            "sma50": sma50,
            "sma200": sma200,
            "rsi": rsi,
            "atr": atr,
            "volume_ratio": volume_ratio,
            "dist_sma50_pct": dist_sma50,
            "conditions": conditions,
            "score_components": score_components,
        }

        logger.debug(f"Trend Pullback: signal={signal_detected}, score={total_score}")

        return result
