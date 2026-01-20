"""
Signal scoring system that aggregates strategy results.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd
from loguru import logger

from src.strategies.base import StrategyResult
from src.strategies.trend_pullback import TrendPullbackStrategy
from src.strategies.breakout import BreakoutStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.macd_crossover import MACDCrossoverStrategy
from src.strategies.golden_cross import GoldenCrossStrategy
from src.strategies.volume_breakout import VolumeBreakoutStrategy
from src.indicators.technical import calculate_indicators, get_latest_indicators
from src.data.downloader import get_ticker_info


@dataclass
class TickerAnalysis:
    """Complete analysis result for a ticker."""

    ticker: str
    name: str = ""  # Company name
    date: Optional[pd.Timestamp] = None

    # Price data
    close: float = 0.0
    change_1d_pct: float = 0.0

    # Global score
    global_score: int = 0
    best_strategy: str = ""

    # Individual strategy results
    strategy_results: Dict[str, StrategyResult] = field(default_factory=dict)

    # Technical levels from best strategy
    entry_level: Optional[float] = None
    invalidation_level: Optional[float] = None
    target_level: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # Key metrics
    rsi: Optional[float] = None
    atr_pct: Optional[float] = None
    volume_ratio: Optional[float] = None
    dist_sma200_pct: Optional[float] = None

    # Summary
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    risk_summary: str = ""
    novice_summary: str = ""  # Résumé en langage simple pour débutants

    # Visual indicators for novices
    trend_status: str = ""  # 🟢 Haussier / 🔴 Baissier / 🟡 Neutre
    momentum_status: str = ""  # État du RSI
    volatility_status: str = ""  # Niveau de volatilité
    volume_status: str = ""  # État du volume
    overall_status: str = ""  # Résumé global

    # Global verdict
    verdict: str = ""  # Verdict global en une phrase
    verdict_emoji: str = ""  # Emoji du verdict
    verdict_detail: str = ""  # Explication détaillée du verdict
    action_suggestion: str = ""  # Suggestion d'action (surveiller, attendre, etc.)

    # Status
    has_signal: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame export."""
        return {
            "ticker": self.ticker,
            "date": self.date,
            "close": self.close,
            "change_1d_pct": self.change_1d_pct,
            "global_score": self.global_score,
            "best_strategy": self.best_strategy,
            "entry_level": self.entry_level,
            "invalidation_level": self.invalidation_level,
            "target_level": self.target_level,
            "risk_reward": self.risk_reward_ratio,
            "rsi": self.rsi,
            "atr_pct": self.atr_pct,
            "volume_ratio": self.volume_ratio,
            "dist_sma200_pct": self.dist_sma200_pct,
            "has_signal": self.has_signal,
            "main_reason": self.reasons[0] if self.reasons else "",
        }


class SignalScorer:
    """
    Aggregates multiple strategy results into a global score.

    Scoring logic:
    - Global score = max(strategy scores)
    - Bonus +10 if 2 strategies signal
    - Bonus +15 if 3 strategies signal
    """

    def __init__(self):
        """Initialize scorer with all strategies."""
        self.strategies = {
            "trend_pullback": TrendPullbackStrategy(),
            "breakout": BreakoutStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "macd_crossover": MACDCrossoverStrategy(),
            "golden_cross": GoldenCrossStrategy(),
            "volume_breakout": VolumeBreakoutStrategy(),
        }

    def analyze_ticker(self, df: pd.DataFrame, ticker: str) -> TickerAnalysis:
        """
        Run full analysis on a ticker's price data.

        Args:
            df: DataFrame with OHLCV data
            ticker: Ticker symbol

        Returns:
            TickerAnalysis with all results
        """
        analysis = TickerAnalysis(ticker=ticker)

        # Try to get company name
        try:
            info = get_ticker_info(ticker)
            if info:
                analysis.name = info.get("name", ticker)
            else:
                analysis.name = ticker
        except Exception:
            analysis.name = ticker

        if df is None or df.empty:
            analysis.error = "No data available"
            return analysis

        try:
            # Calculate indicators if not already done
            if "SMA200" not in df.columns:
                df = calculate_indicators(df)

            # Get latest data point info
            latest = df.iloc[-1]
            analysis.date = df.index[-1]
            analysis.close = latest["Close"]
            analysis.change_1d_pct = latest.get("Return_1d", 0)
            analysis.rsi = latest.get("RSI")
            analysis.atr_pct = latest.get("ATR_pct")
            analysis.volume_ratio = latest.get("Volume_ratio")
            analysis.dist_sma200_pct = latest.get("Dist_SMA200_pct")

            # Run all strategies
            signals_detected = 0
            max_score = 0
            best_strategy_name = ""

            for name, strategy in self.strategies.items():
                result = strategy.evaluate(df)
                analysis.strategy_results[name] = result

                if result.signal_detected:
                    signals_detected += 1

                if result.score > max_score:
                    max_score = result.score
                    best_strategy_name = result.strategy_name

                # Collect all reasons and warnings
                analysis.reasons.extend(result.reasons)
                analysis.warnings.extend(result.warnings)

            # Calculate global score with bonus for multiple signals
            bonus = 0
            if signals_detected >= 3:
                bonus = 15
                analysis.reasons.insert(0, "⭐ Confluence: 3 stratégies en signal")
            elif signals_detected == 2:
                bonus = 10
                analysis.reasons.insert(0, "⭐ Confluence: 2 stratégies en signal")

            analysis.global_score = min(100, max_score + bonus)
            analysis.best_strategy = best_strategy_name
            analysis.has_signal = signals_detected > 0

            # Get technical levels from best strategy
            if best_strategy_name:
                for name, result in analysis.strategy_results.items():
                    if result.strategy_name == best_strategy_name and result.signal_detected:
                        analysis.entry_level = result.entry_level
                        analysis.invalidation_level = result.invalidation_level
                        analysis.target_level = result.target_level
                        analysis.risk_reward_ratio = result.risk_reward_ratio
                        break

            # Generate risk summary
            analysis.risk_summary = self._generate_risk_summary(analysis)

            # Generate novice-friendly indicators and summary
            self._generate_novice_indicators(analysis)
            analysis.novice_summary = self._generate_novice_summary(analysis)

            # Generate global verdict
            self._generate_verdict(analysis)

            logger.debug(f"{ticker}: score={analysis.global_score}, strategy={best_strategy_name}")

        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            analysis.error = str(e)

        return analysis

    def _generate_risk_summary(self, analysis: TickerAnalysis) -> str:
        """Generate a risk summary text."""
        risks = []

        # Volatility risk
        if analysis.atr_pct:
            if analysis.atr_pct > 5:
                risks.append("Volatilité très élevée")
            elif analysis.atr_pct > 3:
                risks.append("Volatilité élevée")

        # Trend risk
        if analysis.dist_sma200_pct:
            if analysis.dist_sma200_pct < 0:
                risks.append("Prix sous SMA200 (tendance baissière)")
            elif analysis.dist_sma200_pct > 20:
                risks.append("Prix très éloigné de SMA200 (potentiel excès)")

        # RSI extremes
        if analysis.rsi:
            if analysis.rsi > 80:
                risks.append("RSI en surachat")
            elif analysis.rsi < 20:
                risks.append("RSI en forte survente")

        # Volume
        if analysis.volume_ratio and analysis.volume_ratio < 0.5:
            risks.append("Volume très faible")

        if not risks:
            return "Aucun risque majeur identifié"

        return " | ".join(risks)

    def _generate_novice_indicators(self, analysis: TickerAnalysis) -> None:
        """Generate visual indicators for novices."""

        # Trend status based on SMA200
        if analysis.dist_sma200_pct is not None:
            if analysis.dist_sma200_pct > 5:
                analysis.trend_status = "🟢 Haussier"
            elif analysis.dist_sma200_pct > 0:
                analysis.trend_status = "🟡 Légèrement haussier"
            elif analysis.dist_sma200_pct > -5:
                analysis.trend_status = "🟡 Légèrement baissier"
            else:
                analysis.trend_status = "🔴 Baissier"
        else:
            analysis.trend_status = "⚪ Indéterminé"

        # Momentum status based on RSI
        if analysis.rsi is not None:
            if analysis.rsi >= 70:
                analysis.momentum_status = "🔴 Surachat (attention)"
            elif analysis.rsi >= 60:
                analysis.momentum_status = "🟢 Fort momentum"
            elif analysis.rsi >= 40:
                analysis.momentum_status = "🟡 Neutre"
            elif analysis.rsi >= 30:
                analysis.momentum_status = "🟡 Faible momentum"
            else:
                analysis.momentum_status = "🟢 Survente (opportunité?)"
        else:
            analysis.momentum_status = "⚪ Indéterminé"

        # Volatility status based on ATR%
        if analysis.atr_pct is not None:
            if analysis.atr_pct >= 5:
                analysis.volatility_status = "🔴 Très volatile (risqué)"
            elif analysis.atr_pct >= 3:
                analysis.volatility_status = "🟡 Volatile"
            elif analysis.atr_pct >= 1.5:
                analysis.volatility_status = "🟢 Normale"
            else:
                analysis.volatility_status = "🔵 Calme"
        else:
            analysis.volatility_status = "⚪ Indéterminé"

        # Volume status
        if analysis.volume_ratio is not None:
            if analysis.volume_ratio >= 2:
                analysis.volume_status = "🟢 Volume très fort"
            elif analysis.volume_ratio >= 1.5:
                analysis.volume_status = "🟢 Volume élevé"
            elif analysis.volume_ratio >= 0.8:
                analysis.volume_status = "🟡 Volume normal"
            else:
                analysis.volume_status = "🔴 Volume faible"
        else:
            analysis.volume_status = "⚪ Indéterminé"

        # Overall status based on score
        if analysis.global_score >= 80:
            analysis.overall_status = "🌟 Signal fort"
        elif analysis.global_score >= 60:
            analysis.overall_status = "✅ Signal intéressant"
        elif analysis.global_score >= 40:
            analysis.overall_status = "🟡 À surveiller"
        else:
            analysis.overall_status = "⚪ Pas de signal"

    def _generate_verdict(self, analysis: TickerAnalysis) -> None:
        """Generate a global verdict with actionable insight."""

        score = analysis.global_score
        has_signal = analysis.has_signal
        strategy = analysis.best_strategy
        rsi = analysis.rsi or 50
        atr_pct = analysis.atr_pct or 2
        volume_ratio = analysis.volume_ratio or 1
        dist_sma200 = analysis.dist_sma200_pct or 0

        # Count positive and negative factors
        positives = 0
        negatives = 0

        # Trend factor
        if dist_sma200 > 5:
            positives += 2
        elif dist_sma200 > 0:
            positives += 1
        elif dist_sma200 < -10:
            negatives += 2
        elif dist_sma200 < 0:
            negatives += 1

        # RSI factor
        if 40 <= rsi <= 60:
            positives += 1  # Neutral is good for entries
        elif rsi > 75:
            negatives += 2  # Overbought risk
        elif rsi < 25:
            positives += 1  # Oversold opportunity
            negatives += 1  # But also risky

        # Volume factor
        if volume_ratio >= 1.5:
            positives += 1
        elif volume_ratio < 0.5:
            negatives += 1

        # Volatility factor
        if atr_pct > 5:
            negatives += 1  # High risk
        elif atr_pct < 1:
            negatives += 1  # Too flat

        # Risk/Reward factor
        if analysis.risk_reward_ratio:
            if analysis.risk_reward_ratio >= 2:
                positives += 2
            elif analysis.risk_reward_ratio >= 1.5:
                positives += 1
            elif analysis.risk_reward_ratio < 1:
                negatives += 1

        # Generate verdict based on score and factors
        if score >= 80 and has_signal:
            analysis.verdict_emoji = "🌟"
            analysis.verdict = "Configuration technique favorable"
            analysis.verdict_detail = f"""
**Analyse globale positive** - Ce ticker présente une configuration technique intéressante avec un score de {score}/100.

**Points forts identifiés:**
- Signal {strategy} détecté avec conviction
- {"Tendance de fond haussière" if dist_sma200 > 0 else "Potentiel de rebond"}
- {"Volume confirmant le mouvement" if volume_ratio >= 1.5 else "Dynamique en place"}
- {"Ratio risque/récompense favorable" if analysis.risk_reward_ratio and analysis.risk_reward_ratio >= 1.5 else ""}

**Ce que ça signifie:** Les conditions techniques sont réunies pour le setup "{strategy}".
C'est le type de configuration que les traders techniques recherchent.
"""
            if analysis.risk_reward_ratio and analysis.risk_reward_ratio >= 2:
                analysis.action_suggestion = "📋 Configuration à étudier en priorité - Définir vos niveaux personnels avant toute décision"
            else:
                analysis.action_suggestion = "📋 Configuration intéressante - Vérifier que le ratio R/R vous convient"

        elif score >= 60 and has_signal:
            analysis.verdict_emoji = "✅"
            analysis.verdict = "Configuration technique correcte"
            analysis.verdict_detail = f"""
**Analyse globale modérée** - Score de {score}/100, signal {strategy} détecté.

**Situation:**
- Le setup est présent mais {"pas optimal" if negatives > positives else "avec quelques réserves"}
- {"Tendance favorable" if dist_sma200 > 0 else "Contexte de tendance à surveiller"}
- {"Attention à la volatilité élevée" if atr_pct > 4 else "Volatilité acceptable"}

**Ce que ça signifie:** La configuration est intéressante mais présente quelques points d'attention.
{"Le RSI en zone extrême suggère de la prudence." if rsi > 70 or rsi < 30 else ""}
{"Le volume pourrait être plus convaincant." if volume_ratio < 1.2 else ""}
"""
            analysis.action_suggestion = "👀 À surveiller - Attendre éventuellement une meilleure confirmation"

        elif score >= 40:
            analysis.verdict_emoji = "🟡"
            analysis.verdict = "Configuration en développement"
            analysis.verdict_detail = f"""
**Analyse globale neutre** - Score de {score}/100, les conditions ne sont pas encore réunies.

**Situation actuelle:**
- Certains éléments sont positifs, d'autres manquent
- {"Prix en tendance haussière" if dist_sma200 > 0 else "Prix sous la tendance long terme"}
- {"Momentum correct" if 40 <= rsi <= 60 else f"RSI à {rsi:.0f} - zone {'surachat' if rsi > 70 else 'survente' if rsi < 30 else 'neutre'}"}

**Ce que ça signifie:** Ce n'est pas le moment idéal selon les critères techniques.
Le setup pourrait se développer dans les prochains jours.
"""
            analysis.action_suggestion = "⏳ Mettre en watchlist - Pas de précipitation, attendre que les conditions s'améliorent"

        else:
            analysis.verdict_emoji = "⚪"
            analysis.verdict = "Pas de configuration technique"
            analysis.verdict_detail = f"""
**Analyse globale négative** - Score de {score}/100, aucun signal détecté.

**Constat:**
- Les conditions des 3 stratégies (Trend Pullback, Breakout, Mean Reversion) ne sont pas réunies
- {"Tendance baissière" if dist_sma200 < -5 else "Tendance incertaine" if dist_sma200 < 5 else "Tendance ok mais timing pas optimal"}
- {"Volume insuffisant" if volume_ratio < 0.8 else "Volume ok"}

**Ce que ça signifie:** D'un point de vue technique, ce n'est pas le moment.
Cela ne dit rien sur la qualité de l'entreprise, juste sur le timing technique.
"""
            analysis.action_suggestion = "⏸️ Patienter - Les conditions techniques ne sont pas favorables actuellement"

        # Add risk warning based on specific conditions
        risk_warnings = []
        if atr_pct > 5:
            risk_warnings.append("⚠️ Volatilité très élevée - Risque de mouvements brusques")
        if rsi > 80:
            risk_warnings.append("⚠️ RSI en surachat extrême - Risque de correction")
        if rsi < 20:
            risk_warnings.append("⚠️ RSI en survente extrême - L'action peut continuer à baisser")
        if dist_sma200 < -20:
            risk_warnings.append("⚠️ Prix très éloigné de la moyenne - Tendance baissière prononcée")
        if volume_ratio < 0.3:
            risk_warnings.append("⚠️ Volume très faible - Liquidité potentiellement réduite")

        if risk_warnings:
            analysis.verdict_detail += "\n\n**⚠️ Alertes spécifiques:**\n" + "\n".join(risk_warnings)

    def _generate_novice_summary(self, analysis: TickerAnalysis) -> str:
        """Generate a plain-language summary for beginners."""
        parts = []

        # Introduction
        ticker = analysis.ticker
        price = analysis.close
        parts.append(f"📊 **{ticker}** se négocie actuellement à **{price:.2f}**.")

        # Trend explanation
        if analysis.dist_sma200_pct is not None:
            dist = analysis.dist_sma200_pct
            if dist > 10:
                parts.append(f"📈 **Tendance forte à la hausse**: Le prix est {dist:.1f}% au-dessus de sa moyenne long terme (SMA200). L'action est dans une belle dynamique haussière.")
            elif dist > 0:
                parts.append(f"📈 **Tendance haussière**: Le prix est {dist:.1f}% au-dessus de sa moyenne long terme. La tendance est positive.")
            elif dist > -10:
                parts.append(f"📉 **Tendance baissière**: Le prix est {abs(dist):.1f}% en dessous de sa moyenne long terme. Prudence recommandée.")
            else:
                parts.append(f"📉 **Tendance fortement baissière**: Le prix est {abs(dist):.1f}% sous sa moyenne long terme. L'action traverse une période difficile.")

        # RSI explanation
        if analysis.rsi is not None:
            rsi = analysis.rsi
            if rsi >= 70:
                parts.append(f"⚠️ **Surachat** (RSI: {rsi:.0f}): L'action a beaucoup monté récemment. Elle pourrait avoir besoin de souffler ou corriger.")
            elif rsi <= 30:
                parts.append(f"💡 **Survente** (RSI: {rsi:.0f}): L'action a beaucoup baissé. C'est parfois une opportunité, mais attention aux couteaux qui tombent!")
            elif rsi >= 50:
                parts.append(f"✅ **Momentum positif** (RSI: {rsi:.0f}): L'action montre une dynamique favorable.")
            else:
                parts.append(f"⚡ **Momentum faible** (RSI: {rsi:.0f}): L'action manque de force actuellement.")

        # Volume explanation
        if analysis.volume_ratio is not None:
            vol = analysis.volume_ratio
            if vol >= 2:
                parts.append(f"🔊 **Volume explosif** ({vol:.1f}x la normale): Beaucoup d'activité aujourd'hui! Les investisseurs s'intéressent à cette action.")
            elif vol >= 1.5:
                parts.append(f"📢 **Volume élevé** ({vol:.1f}x la normale): Plus d'intérêt que d'habitude pour cette action.")
            elif vol < 0.5:
                parts.append(f"🔇 **Volume très faible** ({vol:.1f}x la normale): Peu d'intérêt des investisseurs aujourd'hui.")

        # Volatility warning
        if analysis.atr_pct is not None:
            atr = analysis.atr_pct
            if atr >= 5:
                parts.append(f"⚠️ **Très volatile** (ATR: {atr:.1f}%): Cette action peut bouger de {atr:.1f}% par jour en moyenne. Réservé aux investisseurs avertis!")
            elif atr >= 3:
                parts.append(f"🎢 **Volatile** (ATR: {atr:.1f}%): Mouvements journaliers importants, adaptez la taille de position.")

        # Signal explanation
        if analysis.has_signal:
            strategy = analysis.best_strategy
            score = analysis.global_score

            if strategy == "Trend Pullback":
                parts.append(f"🎯 **Signal Trend Pullback** (Score: {score}/100): L'action est en tendance haussière et revient vers un niveau de support (SMA50). C'est comme acheter en soldes dans une boutique qui marche bien!")
            elif strategy == "Breakout":
                parts.append(f"🚀 **Signal Breakout** (Score: {score}/100): L'action casse ses plus hauts récents avec du volume. C'est un signe de force, comme un sportif qui bat son record!")
            elif strategy == "Mean Reversion":
                parts.append(f"🔄 **Signal Mean Reversion** (Score: {score}/100): L'action semble survendue et commence à rebondir. C'est comme un élastique trop étiré qui revient vers le centre.")

            # Levels explanation
            if analysis.entry_level and analysis.invalidation_level and analysis.target_level:
                risk_pct = abs((analysis.invalidation_level - analysis.close) / analysis.close * 100)
                reward_pct = abs((analysis.target_level - analysis.close) / analysis.close * 100)
                parts.append(f"📐 **Niveaux indicatifs**: Entrée ~{analysis.entry_level:.2f}, Stop ~{analysis.invalidation_level:.2f} (-{risk_pct:.1f}%), Objectif ~{analysis.target_level:.2f} (+{reward_pct:.1f}%)")
        else:
            parts.append("ℹ️ **Pas de signal actif**: Les conditions ne sont pas réunies pour les stratégies surveillées. L'action reste à surveiller.")

        # Risk reminder
        parts.append("\n⚠️ *Rappel: Ceci est une analyse technique automatique, pas un conseil d'investissement. Faites toujours vos propres recherches!*")

        return "\n\n".join(parts)

    def analyze_watchlist(
        self,
        data: Dict[str, pd.DataFrame],
        min_score: int = 0,
        progress_callback: Optional[callable] = None
    ) -> List[TickerAnalysis]:
        """
        Analyze multiple tickers.

        Args:
            data: Dict mapping ticker to DataFrame
            min_score: Minimum score to include in results
            progress_callback: Optional callback (ticker, current, total)

        Returns:
            List of TickerAnalysis sorted by global_score descending
        """
        results = []
        total = len(data)

        for i, (ticker, df) in enumerate(data.items()):
            if progress_callback:
                progress_callback(ticker, i + 1, total)

            analysis = self.analyze_ticker(df, ticker)

            if analysis.global_score >= min_score:
                results.append(analysis)

        # Sort by global score descending
        results.sort(key=lambda x: x.global_score, reverse=True)

        logger.info(f"Analyzed {total} tickers, {len(results)} with score >= {min_score}")

        return results


def results_to_dataframe(results: List[TickerAnalysis]) -> pd.DataFrame:
    """Convert list of TickerAnalysis to DataFrame."""
    if not results:
        return pd.DataFrame()

    data = [r.to_dict() for r in results]
    df = pd.DataFrame(data)

    # Round numeric columns
    numeric_cols = ["close", "change_1d_pct", "rsi", "atr_pct", "volume_ratio",
                    "dist_sma200_pct", "entry_level", "invalidation_level",
                    "target_level", "risk_reward"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].round(2)

    return df
