"""
Volume Breakout Strategy - Price breakout with volume explosion.
"""
import pandas as pd
from dataclasses import dataclass

from src.strategies.base import BaseStrategy, StrategyResult
from config.settings import get_settings


class VolumeBreakoutStrategy(BaseStrategy):
    """
    Volume Breakout Strategy - Combines price breakout with volume surge.

    Signal when:
    - Price breaks recent high (20-day)
    - Volume explosion (> 2x average)
    - Strong momentum (RSI > 60)
    - Uptrend context (SMA50 > SMA200)
    """

    name = "Volume Breakout"
    description = "Price breakout with volume explosion and strong momentum"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Analyze data for Volume Breakout signal.

        Args:
            df: DataFrame with price data and indicators

        Returns:
            StrategyResult with signal and details
        """
        result = StrategyResult(strategy_name=self.name)

        if len(df) < 60:
            result.warnings.append("Pas assez de données (< 60 jours)")
            return result

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Extract data
        close = latest["Close"]
        volume = latest["Volume"]
        high = latest["High"]

        # Calculate 20-day high
        high_20d = df["High"].iloc[-20:].max()
        high_20d_prev = df["High"].iloc[-21:-1].max()

        volume_avg20 = latest.get("Volume_avg20")
        volume_ratio = latest.get("Volume_ratio")
        rsi = latest.get("RSI")
        sma50 = latest.get("SMA50")
        sma200 = latest.get("SMA200")
        atr_pct = latest.get("ATR_pct")

        # Check for missing data
        if pd.isna(volume_avg20):
            result.warnings.append("Indicateurs de volume manquants")
            return result

        # Calculate score components
        score = 0

        # 1. Price breakout (30 points)
        breakout_detected = False
        if high > high_20d_prev:
            breakout_detected = True
            breakout_pct = ((high - high_20d_prev) / high_20d_prev) * 100

            if breakout_pct > 3:
                score += 30
                result.reasons.append(f"⭐ Breakout fort ! +{breakout_pct:.1f}% vs high 20j")
            elif breakout_pct > 1:
                score += 25
                result.reasons.append(f"✅ Breakout de {breakout_pct:.1f}%")
            else:
                score += 15
                result.reasons.append(f"Breakout léger ({breakout_pct:.1f}%)")

        # 2. Volume explosion (35 points) - Critical for this strategy
        if not pd.isna(volume_ratio):
            if volume_ratio > 3.0:
                score += 35
                result.reasons.append(f"🔥 EXPLOSION DE VOLUME ! {volume_ratio:.1f}x")
            elif volume_ratio > 2.0:
                score += 30
                result.reasons.append(f"✅ Volume très fort ({volume_ratio:.1f}x)")
            elif volume_ratio > 1.5:
                score += 20
                result.reasons.append(f"Volume élevé ({volume_ratio:.1f}x)")
            elif volume_ratio > 1.0:
                score += 10
                result.warnings.append(f"Volume faible pour un breakout ({volume_ratio:.1f}x)")
            else:
                result.warnings.append(f"⚠️ Volume insuffisant ({volume_ratio:.1f}x)")

        # 3. RSI momentum (15 points)
        if not pd.isna(rsi):
            if rsi > 70:
                score += 15
                result.reasons.append(f"Momentum très fort (RSI {rsi:.0f})")
            elif rsi > 60:
                score += 12
                result.reasons.append(f"Bon momentum (RSI {rsi:.0f})")
            elif rsi > 50:
                score += 8
                result.reasons.append(f"Momentum positif (RSI {rsi:.0f})")
            else:
                result.warnings.append(f"Momentum faible (RSI {rsi:.0f})")

        # 4. Trend context (10 points)
        if not pd.isna(sma50) and not pd.isna(sma200):
            if sma50 > sma200:
                score += 10
                result.reasons.append("Contexte haussier (SMA50 > SMA200)")
            else:
                result.warnings.append("Contexte baissier (SMA50 < SMA200)")

        # 5. Volatility (10 points)
        if not pd.isna(atr_pct):
            if 2.0 < atr_pct < 6.0:
                score += 10
                result.reasons.append(f"Volatilité adaptée ({atr_pct:.1f}%)")
            elif atr_pct >= 6.0:
                score += 5
                result.warnings.append(f"Volatilité élevée ({atr_pct:.1f}%)")

        result.score = score

        # Generate signal
        # Requires both breakout AND strong volume
        if breakout_detected and volume_ratio and volume_ratio > 1.5 and score >= 65:
            result.signal_detected = True

            result.entry_level = close

            # Stop below recent low or 2x ATR
            low_3d = df["Low"].iloc[-3:].min()
            atr = latest.get("ATR", close * 0.02)
            stop_option1 = low_3d * 0.99
            stop_option2 = close - (2 * atr)
            result.invalidation_level = max(stop_option1, stop_option2)

            # Target = Risk * 2.5 (volume breakouts can move fast)
            risk = close - result.invalidation_level
            result.target_level = close + (risk * 2.5)

            result.risk_reward_ratio = 2.5

            result.reasons.insert(0, "⭐ Signal Volume Breakout - Fort potentiel momentum")

        elif breakout_detected and (not volume_ratio or volume_ratio < 1.5):
            result.warnings.append("Breakout sans volume - Signal faible")
        elif volume_ratio and volume_ratio > 2.0 and not breakout_detected:
            result.warnings.append("Volume fort mais pas de breakout prix")

        return result
