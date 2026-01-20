"""
Golden Cross Strategy - SMA50 crosses above SMA200.
"""
import pandas as pd
from dataclasses import dataclass

from src.strategies.base import BaseStrategy, StrategyResult
from config.settings import get_settings


class GoldenCrossStrategy(BaseStrategy):
    """
    Golden Cross Strategy - Long-term bullish signal.

    Signal when:
    - SMA50 crosses above SMA200 (golden cross)
    - Price above both SMAs
    - Volume confirmation
    - RSI showing strength
    """

    name = "Golden Cross"
    description = "SMA50 crosses above SMA200 - long-term bullish signal"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Analyze data for Golden Cross signal.

        Args:
            df: DataFrame with price data and indicators

        Returns:
            StrategyResult with signal and details
        """
        result = StrategyResult(strategy_name=self.name)

        if len(df) < 200:
            result.warnings.append("Pas assez de données (< 200 jours)")
            return result

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Extract indicators
        sma50 = latest.get("SMA50")
        sma200 = latest.get("SMA200")
        sma50_prev = prev.get("SMA50")
        sma200_prev = prev.get("SMA200")

        close = latest["Close"]
        rsi = latest.get("RSI")
        volume_ratio = latest.get("Volume_ratio")
        atr_pct = latest.get("ATR_pct")

        # Check for missing data
        if pd.isna(sma50) or pd.isna(sma200):
            result.warnings.append("SMA50 ou SMA200 manquants")
            return result

        # Calculate score components
        score = 0

        # 1. Golden Cross detection (40 points)
        golden_cross = False
        if not pd.isna(sma50_prev) and not pd.isna(sma200_prev):
            # Recent golden cross (within last few days)
            if sma50 > sma200 and sma50_prev <= sma200_prev:
                golden_cross = True
                score += 40
                result.reasons.append("⭐ GOLDEN CROSS ! SMA50 vient de croiser SMA200")
            elif sma50 > sma200:
                # Already in golden cross
                days_above = 0
                for i in range(len(df)-1, max(len(df)-30, 0), -1):
                    if df.iloc[i].get("SMA50") > df.iloc[i].get("SMA200"):
                        days_above += 1
                    else:
                        break

                if days_above <= 10:
                    score += 30
                    result.reasons.append(f"✅ Golden Cross récent ({days_above}j)")
                elif days_above <= 30:
                    score += 20
                    result.reasons.append(f"Golden Cross en cours ({days_above}j)")
                else:
                    score += 10
                    result.reasons.append(f"Golden Cross ancien ({days_above}j+)")
        else:
            # Death cross (bearish)
            if sma50 < sma200:
                result.warnings.append("⚠️ Death Cross - SMA50 sous SMA200")

        # 2. Price position (25 points)
        if close > sma50 and close > sma200:
            dist_50 = ((close - sma50) / sma50) * 100
            dist_200 = ((close - sma200) / sma200) * 100

            if dist_50 > 5 and dist_200 > 10:
                score += 25
                result.reasons.append(f"✅ Prix bien au-dessus des 2 SMAs")
            elif dist_50 > 0 and dist_200 > 0:
                score += 15
                result.reasons.append(f"Prix au-dessus des 2 SMAs")
        elif close > sma50:
            score += 10
            result.warnings.append("Prix au-dessus SMA50 mais sous SMA200")
        else:
            result.warnings.append("⚠️ Prix sous SMA50")

        # 3. RSI (15 points)
        if not pd.isna(rsi):
            if 50 < rsi < 70:
                score += 15
                result.reasons.append(f"RSI haussier ({rsi:.0f})")
            elif rsi >= 70:
                score += 8
                result.warnings.append(f"RSI surachat ({rsi:.0f})")
            elif rsi > 40:
                score += 5
                result.reasons.append(f"RSI neutre ({rsi:.0f})")

        # 4. Volume confirmation (10 points)
        if not pd.isna(volume_ratio):
            if volume_ratio > 1.2:
                score += 10
                result.reasons.append(f"Volume fort ({volume_ratio:.1f}x)")
            elif volume_ratio > 0.8:
                score += 5

        # 5. Volatility (10 points)
        if not pd.isna(atr_pct):
            if 1.0 < atr_pct < 4.0:
                score += 10
                result.reasons.append(f"Volatilité saine ({atr_pct:.1f}%)")
            elif atr_pct < 1.0:
                score += 5

        result.score = score

        # Generate signal
        if (golden_cross or (sma50 > sma200 and score >= 70)) and close > sma50:
            result.signal_detected = True

            result.entry_level = close

            # Conservative stop for long-term trade
            # Stop below SMA200 or 2.5x ATR
            atr = latest.get("ATR", close * 0.02)
            stop_option1 = sma200 * 0.98  # 2% below SMA200
            stop_option2 = close - (2.5 * atr)
            result.invalidation_level = max(stop_option1, stop_option2)

            # Target = Risk * 2 (conservative for long-term)
            risk = close - result.invalidation_level
            result.target_level = close + (risk * 2)

            result.risk_reward_ratio = 2.0

            result.reasons.insert(0, "⭐ Signal Golden Cross - Tendance haussière long terme")

        elif sma50 > sma200 and score < 70:
            result.warnings.append("Golden Cross présent mais conditions faibles")

        return result
