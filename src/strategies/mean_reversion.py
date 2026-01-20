"""
Mean Reversion Strategy.

Detects oversold conditions with potential reversal signals.
Conditions:
- Close < Lower Bollinger Band (oversold)
- RSI < 30 (oversold confirmation)
- Price starts to recover (close > BB lower next day)
"""
import pandas as pd
from loguru import logger

from config.settings import get_settings
from src.strategies.base import BaseStrategy, StrategyResult


class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion strategy implementation."""

    name = "Mean Reversion"
    description = "Oversold bounce from lower Bollinger Band with RSI confirmation"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Evaluate Mean Reversion conditions.

        Args:
            df: DataFrame with indicators

        Returns:
            StrategyResult with signal and scoring
        """
        result = StrategyResult(strategy_name=self.name)

        if not self._check_data_validity(df):
            result.warnings.append("Insufficient data for analysis")
            return result

        # Check for Bollinger Band columns
        if "BB_lower" not in df.columns:
            result.warnings.append("Bollinger Bands not calculated")
            return result

        # Get latest and previous values
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        prev2 = df.iloc[-3] if len(df) > 2 else prev

        close = latest["Close"]
        close_prev = prev["Close"]
        bb_lower = latest["BB_lower"]
        bb_lower_prev = prev["BB_lower"]
        bb_middle = latest["BB_middle"]
        rsi = latest["RSI"]
        rsi_prev = prev["RSI"]
        atr = latest["ATR"]
        volume_ratio = latest["Volume_ratio"]
        sma200 = latest["SMA200"]

        # Track conditions
        conditions = {}
        score_components = {}

        # Condition 1: Price was below or touched lower BB recently
        was_below_bb = (close_prev <= bb_lower_prev) or (prev2["Close"] <= prev2.get("BB_lower", bb_lower_prev) if len(df) > 2 else False)
        conditions["touched_lower_bb"] = was_below_bb or close <= bb_lower

        if close <= bb_lower:
            result.reasons.append(f"Prix sous bande Bollinger basse ({close:.2f} < {bb_lower:.2f})")
            score_components["bb_oversold"] = 30
        elif was_below_bb:
            result.reasons.append("Prix était sous BB basse récemment")
            score_components["bb_oversold"] = 25
        else:
            result.warnings.append("Prix pas en zone de survente BB")
            score_components["bb_oversold"] = 0

        # Condition 2: RSI oversold
        rsi_oversold = rsi < 30 or rsi_prev < 30
        conditions["rsi_oversold"] = rsi_oversold

        if rsi < 25:
            result.reasons.append(f"RSI très survendu ({rsi:.1f})")
            score_components["rsi"] = 30
        elif rsi < 30:
            result.reasons.append(f"RSI survendu ({rsi:.1f})")
            score_components["rsi"] = 25
        elif rsi_prev < 30 and rsi > rsi_prev:
            result.reasons.append(f"RSI en rebond depuis survente ({rsi_prev:.1f} → {rsi:.1f})")
            score_components["rsi"] = 20
        elif rsi < 40:
            result.warnings.append(f"RSI bas mais pas survendu ({rsi:.1f})")
            score_components["rsi"] = 10
        else:
            result.warnings.append(f"RSI pas en zone de survente ({rsi:.1f})")
            score_components["rsi"] = 0

        # Condition 3: Recovery signal (price bouncing back)
        recovering = close > close_prev and close > bb_lower
        conditions["recovering"] = recovering

        if was_below_bb and close > bb_lower:
            result.reasons.append("Signal de rebond: prix repasse au-dessus de BB basse")
            score_components["recovery"] = 25
        elif close > close_prev:
            result.reasons.append("Prix en hausse aujourd'hui")
            score_components["recovery"] = 15
        else:
            result.warnings.append("Pas encore de signal de rebond")
            score_components["recovery"] = 0

        # Volume consideration
        if volume_ratio >= 1.5:
            result.reasons.append(f"Volume élevé sur rebond ({volume_ratio:.1f}x)")
            score_components["volume"] = 15
        elif volume_ratio >= 1.0:
            score_components["volume"] = 10
        else:
            score_components["volume"] = 5

        # Context: trend
        if close > sma200:
            result.reasons.append("Rebond dans tendance haussière (prix > SMA200)")
            trend_bonus = 10
        else:
            result.warnings.append("Rebond contre tendance - risque plus élevé")
            trend_bonus = 0

        # Calculate total score
        total_score = sum(score_components.values()) + trend_bonus

        # Signal detected if oversold conditions met with recovery
        signal_detected = (
            conditions["touched_lower_bb"] and
            conditions["rsi_oversold"] and
            conditions["recovering"]
        )

        # Calculate technical levels (tighter for mean reversion)
        entry = close
        invalidation = close - (atr * 1.5)  # Tighter stop
        target = bb_middle  # Target middle band
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
            "bb_lower": bb_lower,
            "bb_middle": bb_middle,
            "rsi": rsi,
            "atr": atr,
            "volume_ratio": volume_ratio,
            "sma200": sma200,
            "conditions": conditions,
            "score_components": score_components,
            "trend_bonus": trend_bonus,
        }

        logger.debug(f"Mean Reversion: signal={signal_detected}, score={total_score}")

        return result
