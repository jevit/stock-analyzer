"""
MACD Crossover Strategy - Detect bullish MACD crossovers.
"""
import pandas as pd
from dataclasses import dataclass

from src.strategies.base import BaseStrategy, StrategyResult
from config.settings import get_settings


class MACDCrossoverStrategy(BaseStrategy):
    """
    MACD Crossover Strategy.

    Signal when:
    - MACD line crosses above Signal line (bullish crossover)
    - Price above SMA200 (uptrend)
    - RSI not overbought (< 70)
    """

    name = "MACD Crossover"
    description = "Bullish MACD crossover in uptrend with RSI confirmation"

    def __init__(self):
        """Initialize strategy with settings."""
        self.settings = get_settings()

    def evaluate(self, df: pd.DataFrame) -> StrategyResult:
        """
        Analyze data for MACD crossover signal.

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
        macd = latest.get("MACD")
        macd_signal = latest.get("MACD_signal")
        macd_prev = prev.get("MACD")
        macd_signal_prev = prev.get("MACD_signal")

        sma200 = latest.get("SMA200")
        close = latest["Close"]
        rsi = latest.get("RSI")
        atr_pct = latest.get("ATR_pct")

        # Check for missing data
        if pd.isna(macd) or pd.isna(macd_signal) or pd.isna(sma200):
            result.warnings.append("Indicateurs MACD ou SMA200 manquants")
            return result

        # Calculate score components
        score = 0

        # 1. MACD Crossover (30 points)
        macd_crossover = False
        if not pd.isna(macd_prev) and not pd.isna(macd_signal_prev):
            if macd > macd_signal and macd_prev <= macd_signal_prev:
                macd_crossover = True
                score += 30
                result.reasons.append("✅ MACD vient de croiser au-dessus de sa signal")
            elif macd > macd_signal:
                score += 15
                result.reasons.append("MACD au-dessus de sa signal (pas de croisement récent)")

        # 2. Price above SMA200 (25 points)
        if close > sma200:
            dist_pct = ((close - sma200) / sma200) * 100
            if dist_pct > 10:
                score += 25
                result.reasons.append(f"✅ Prix bien au-dessus SMA200 (+{dist_pct:.1f}%)")
            elif dist_pct > 0:
                score += 15
                result.reasons.append(f"Prix au-dessus SMA200 (+{dist_pct:.1f}%)")
        else:
            result.warnings.append("⚠️ Prix sous SMA200 (tendance baissière)")

        # 3. MACD in positive territory (15 points)
        if macd > 0:
            score += 15
            result.reasons.append("MACD en territoire positif")

        # 4. RSI conditions (15 points)
        if not pd.isna(rsi):
            if 50 < rsi < 70:
                score += 15
                result.reasons.append(f"✅ RSI à {rsi:.0f} (haussier mais pas surachat)")
            elif rsi >= 70:
                score += 5
                result.warnings.append(f"⚠️ RSI surachat ({rsi:.0f})")
            elif rsi <= 30:
                result.warnings.append(f"⚠️ RSI survente ({rsi:.0f}) - tendance faible")

        # 5. Volatility check (15 points)
        if not pd.isna(atr_pct):
            if 1.0 < atr_pct < 5.0:
                score += 15
                result.reasons.append(f"Volatilité normale ({atr_pct:.1f}%)")
            elif atr_pct < 1.0:
                score += 5
                result.warnings.append("Volatilité faible (mouvement limité)")
            else:
                result.warnings.append(f"⚠️ Volatilité élevée ({atr_pct:.1f}%)")

        result.score = score

        # Generate signal if conditions met
        if macd_crossover and close > sma200 and score >= 60:
            result.signal_detected = True

            # Entry = current close
            result.entry_level = close

            # Stop = 2x ATR below entry
            atr = latest.get("ATR", close * 0.02)
            result.invalidation_level = close - (2 * atr)

            # Target = Risk * 2
            risk = close - result.invalidation_level
            result.target_level = close + (risk * 2)

            result.risk_reward_ratio = 2.0

            result.reasons.insert(0, "⭐ Signal MACD Crossover haussier détecté")
        elif macd_crossover and score < 60:
            result.warnings.append("Croisement MACD détecté mais score global faible")
        elif close <= sma200:
            result.warnings.append("Pas de signal : prix sous SMA200")

        return result
