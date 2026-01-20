"""
Table components for displaying analysis results.
"""
import pandas as pd
import streamlit as st
from typing import List

from src.scoring.scorer import TickerAnalysis
from app.utils.tooltips import TOOLTIPS


def create_opportunities_table(
    analyses: List[TickerAnalysis],
    show_columns: List[str] = None
) -> pd.DataFrame:
    """
    Create a formatted DataFrame for display.

    Args:
        analyses: List of TickerAnalysis objects
        show_columns: Columns to display (None = default set)

    Returns:
        Formatted DataFrame
    """
    if not analyses:
        return pd.DataFrame()

    # Convert to DataFrame
    data = []
    for a in analyses:
        row = {
            "Ticker": a.ticker,
            "Score": a.global_score,
            "Stratégie": a.best_strategy,
            "Prix": a.close,
            "Var. 1J %": a.change_1d_pct,
            "RSI": a.rsi,
            "ATR %": a.atr_pct,
            "Vol. Ratio": a.volume_ratio,
            "Dist. SMA200 %": a.dist_sma200_pct,
            "Entrée": a.entry_level,
            "Invalidation": a.invalidation_level,
            "Objectif": a.target_level,
            "R/R": a.risk_reward_ratio,
            "Signal": "✅" if a.has_signal else "❌",
        }
        data.append(row)

    df = pd.DataFrame(data)

    # Sort by Score descending (numerically)
    if "Score" in df.columns:
        df = df.sort_values(by="Score", ascending=False)

    # Default columns
    if show_columns is None:
        show_columns = [
            "Ticker", "Score", "Stratégie", "Prix", "RSI",
            "ATR %", "Vol. Ratio", "R/R", "Signal"
        ]

    # Filter and reorder columns
    df = df[[c for c in show_columns if c in df.columns]]

    # Round numeric columns (handle None values)
    numeric_cols = ["Prix", "Var. 1J %", "RSI", "ATR %", "Vol. Ratio",
                    "Dist. SMA200 %", "Entrée", "Invalidation", "Objectif", "R/R"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    return df


def create_novice_table(analyses: List[TickerAnalysis], sort_by_verdict: bool = True) -> pd.DataFrame:
    """
    Create a beginner-friendly table with visual indicators.

    Args:
        analyses: List of TickerAnalysis objects
        sort_by_verdict: Sort by verdict (most favorable first)

    Returns:
        Formatted DataFrame with emojis and simple explanations
    """
    if not analyses:
        return pd.DataFrame()

    data = []
    for a in analyses:
        # Score with visual indicator
        if a.global_score >= 80:
            score_visual = f"🌟 {a.global_score}"
        elif a.global_score >= 60:
            score_visual = f"✅ {a.global_score}"
        elif a.global_score >= 40:
            score_visual = f"🟡 {a.global_score}"
        else:
            score_visual = f"⚪ {a.global_score}"

        # RSI with explanation
        if a.rsi is not None:
            if a.rsi >= 70:
                rsi_visual = f"🔴 {a.rsi:.0f} (surachat)"
            elif a.rsi <= 30:
                rsi_visual = f"🟢 {a.rsi:.0f} (survente)"
            elif a.rsi >= 50:
                rsi_visual = f"🟢 {a.rsi:.0f} (positif)"
            else:
                rsi_visual = f"🟡 {a.rsi:.0f} (faible)"
        else:
            rsi_visual = "—"

        # Volatility with explanation
        if a.atr_pct is not None:
            if a.atr_pct >= 5:
                vol_visual = f"🔴 {a.atr_pct:.1f}% (très risqué)"
            elif a.atr_pct >= 3:
                vol_visual = f"🟡 {a.atr_pct:.1f}% (volatile)"
            elif a.atr_pct >= 1.5:
                vol_visual = f"🟢 {a.atr_pct:.1f}% (normal)"
            else:
                vol_visual = f"🔵 {a.atr_pct:.1f}% (calme)"
        else:
            vol_visual = "—"

        # Volume with explanation
        if a.volume_ratio is not None:
            if a.volume_ratio >= 2:
                volume_visual = f"🟢 {a.volume_ratio:.1f}x (très fort)"
            elif a.volume_ratio >= 1.5:
                volume_visual = f"🟢 {a.volume_ratio:.1f}x (élevé)"
            elif a.volume_ratio >= 0.8:
                volume_visual = f"🟡 {a.volume_ratio:.1f}x (normal)"
            else:
                volume_visual = f"🔴 {a.volume_ratio:.1f}x (faible)"
        else:
            volume_visual = "—"

        # Trend
        if a.dist_sma200_pct is not None:
            if a.dist_sma200_pct > 5:
                trend_visual = "📈 Haussier"
            elif a.dist_sma200_pct > 0:
                trend_visual = "↗️ Légèrement +"
            elif a.dist_sma200_pct > -5:
                trend_visual = "↘️ Légèrement -"
            else:
                trend_visual = "📉 Baissier"
        else:
            trend_visual = "—"

        # Verdict with priority for sorting (0 = best, 3 = worst)
        if a.global_score >= 80 and a.has_signal:
            verdict_mini = "🌟 FAVORABLE"
            verdict_order = 0
        elif a.global_score >= 60 and a.has_signal:
            verdict_mini = "✅ Correct"
            verdict_order = 1
        elif a.global_score >= 40:
            verdict_mini = "👀 Surveiller"
            verdict_order = 2
        else:
            verdict_mini = "⏸️ Attendre"
            verdict_order = 3

        # Build short summary for tooltip
        summary_parts = []
        if a.best_strategy:
            summary_parts.append(f"Signal: {a.best_strategy}")
        if a.reasons:
            main_reason = next((r for r in a.reasons if not r.startswith("⭐")), a.reasons[0] if a.reasons else "")
            if main_reason:
                summary_parts.append(main_reason[:50])
        if a.risk_summary and a.risk_summary != "Aucun risque majeur identifié":
            summary_parts.append(f"⚠️ {a.risk_summary[:40]}")

        summary = " | ".join(summary_parts) if summary_parts else "Pas de signal actif"

        # Format ticker with name
        ticker_display = a.ticker
        name_display = a.name if a.name and a.name != a.ticker else ""

        # Shorten long names
        if len(name_display) > 25:
            name_display = name_display[:22] + "..."

        row = {
            "_verdict_order": verdict_order,  # Hidden column for sorting
            "_score": a.global_score,  # Hidden column for sorting
            "Ticker": ticker_display,
            "Nom": name_display,
            "Verdict": verdict_mini,
            "Score": score_visual,
            "Stratégie": a.best_strategy if a.best_strategy else "—",
            "Prix": f"{a.close:.2f}",
            "Tendance": trend_visual,
            "RSI": rsi_visual,
            "Volatilité": vol_visual,
            "Volume": volume_visual,
            "Résumé": summary,
        }
        data.append(row)

    df = pd.DataFrame(data)

    # Sort by verdict order, then by score descending
    df = df.sort_values(by=["_verdict_order", "_score"], ascending=[True, False])

    # Drop hidden columns
    df = df.drop(columns=["_verdict_order", "_score"])

    return df


def style_opportunities_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """
    Apply styling to the opportunities table.

    Args:
        df: DataFrame to style

    Returns:
        Styled DataFrame
    """
    def color_score(val):
        """Color code based on score value."""
        if pd.isna(val):
            return ""
        # Extract number if string contains emoji
        if isinstance(val, str):
            import re
            match = re.search(r'\d+', val)
            if match:
                val = int(match.group())
            else:
                return ""
        if val >= 80:
            return "background-color: #1b5e20; color: white"
        elif val >= 60:
            return "background-color: #33691e; color: white"
        elif val >= 40:
            return "background-color: #827717; color: white"
        else:
            return "background-color: #4a4a4a"

    def color_change(val):
        """Color positive/negative changes."""
        if pd.isna(val):
            return ""
        if val > 0:
            return "color: #26a69a"
        elif val < 0:
            return "color: #ef5350"
        return ""

    def color_rsi(val):
        """Color RSI based on zones."""
        if pd.isna(val):
            return ""
        if val >= 70:
            return "color: #ef5350"  # Overbought
        elif val <= 30:
            return "color: #26a69a"  # Oversold
        return ""

    # Build styler
    styler = df.style

    if "Score" in df.columns:
        styler = styler.map(color_score, subset=["Score"])

    if "Var. 1J %" in df.columns:
        styler = styler.map(color_change, subset=["Var. 1J %"])

    if "RSI" in df.columns:
        styler = styler.map(color_rsi, subset=["RSI"])

    # Format numbers
    format_dict = {}
    if "Prix" in df.columns:
        format_dict["Prix"] = "{:.2f}"
    if "R/R" in df.columns:
        format_dict["R/R"] = "{:.2f}"

    if format_dict:
        styler = styler.format(format_dict)

    return styler


def render_novice_summary(analysis: TickerAnalysis) -> None:
    """
    Render a beginner-friendly summary card.

    Args:
        analysis: TickerAnalysis object
    """
    st.markdown("### 📖 Résumé pour débutants")

    # Status indicators in a nice grid
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Tendance** ℹ️")
        st.markdown(f"### {analysis.trend_status}")
        with st.expander("💡 C'est quoi?", expanded=False):
            st.markdown(TOOLTIPS.get("SMA200", "Tendance basée sur la moyenne mobile 200 jours"))

    with col2:
        st.markdown("**Momentum** ℹ️")
        st.markdown(f"### {analysis.momentum_status}")
        with st.expander("💡 C'est quoi?", expanded=False):
            st.markdown(TOOLTIPS.get("RSI", "Force du mouvement des prix"))

    with col3:
        st.markdown("**Volatilité** ℹ️")
        st.markdown(f"### {analysis.volatility_status}")
        with st.expander("💡 C'est quoi?", expanded=False):
            st.markdown(TOOLTIPS.get("ATR_PCT", "Amplitude moyenne des mouvements"))

    with col4:
        st.markdown("**Volume** ℹ️")
        st.markdown(f"### {analysis.volume_status}")
        with st.expander("💡 C'est quoi?", expanded=False):
            st.markdown(TOOLTIPS.get("VOLUME", "Activité des transactions"))

    st.markdown("---")

    # Overall status
    st.markdown(f"### {analysis.overall_status}")

    # Detailed summary in expandable section
    with st.expander("📝 Explication détaillée", expanded=True):
        st.markdown(analysis.novice_summary)


def render_indicator_legend() -> None:
    """Render a legend explaining the indicators."""
    with st.expander("❓ Guide de lecture des indicateurs", expanded=False):
        st.markdown("""
        ### Comprendre les indicateurs

        #### 🎯 Score (0-100)
        | Score | Signification |
        |-------|---------------|
        | 🌟 80+ | Signal très fort - Toutes les conditions sont réunies |
        | ✅ 60-79 | Signal intéressant - La plupart des conditions sont bonnes |
        | 🟡 40-59 | À surveiller - Quelques éléments positifs |
        | ⚪ 0-39 | Pas de signal - Conditions non réunies |

        #### 📈 Tendance (basée sur SMA200)
        La moyenne mobile 200 jours indique la tendance de fond:
        - **📈 Haussier**: Prix bien au-dessus → L'action est en forme!
        - **📉 Baissier**: Prix en dessous → Prudence recommandée

        #### ⚡ Momentum / RSI (0-100)
        Le RSI mesure la "vitesse" du mouvement:
        - **🔴 >70 (Surachat)**: L'action a beaucoup monté, risque de pause
        - **🟢 <30 (Survente)**: L'action a beaucoup baissé, possible rebond
        - **🟡 30-70**: Zone neutre

        #### 🎢 Volatilité / ATR%
        Indique combien l'action bouge en moyenne par jour:
        - **🔵 <1.5%**: Calme - Petits mouvements
        - **🟢 1.5-3%**: Normal - Mouvements raisonnables
        - **🟡 3-5%**: Volatile - Mouvements importants
        - **🔴 >5%**: Très volatile - Gros risques, gros gains potentiels

        #### 📊 Volume
        Compare le volume du jour à la moyenne:
        - **🟢 >1.5x**: Fort intérêt des investisseurs
        - **🟡 0.8-1.5x**: Activité normale
        - **🔴 <0.8x**: Peu d'intérêt

        #### 📐 R/R (Ratio Reward/Risk)
        Compare le gain potentiel au risque:
        - **>2.0**: Excellent - Vous pouvez gagner 2x plus que vous risquez
        - **1.0-2.0**: Correct - Gain et risque équilibrés
        - **<1.0**: Défavorable - Risque supérieur au gain potentiel
        """)


def render_strategy_details(analysis: TickerAnalysis) -> None:
    """
    Render detailed strategy results in Streamlit.

    Args:
        analysis: TickerAnalysis object
    """
    st.subheader("🔬 Détail des Stratégies")

    # Map strategy names to tooltip keys
    strategy_tooltip_map = {
        "Trend Pullback": "TREND_PULLBACK",
        "Breakout": "BREAKOUT",
        "Mean Reversion": "MEAN_REVERSION",
        "MACD Crossover": "MACD_CROSSOVER",
        "Golden Cross": "GOLDEN_CROSS",
        "Volume Breakout": "VOLUME_BREAKOUT",
    }

    for name, result in analysis.strategy_results.items():
        with st.expander(
            f"{'✅' if result.signal_detected else '❌'} {result.strategy_name} - Score: {result.score}/100",
            expanded=result.signal_detected
        ):
            # Show tooltip explanation if available
            tooltip_key = strategy_tooltip_map.get(result.strategy_name)
            if tooltip_key and tooltip_key in TOOLTIPS:
                st.info(TOOLTIPS[tooltip_key])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**✅ Points positifs:**")
                if result.reasons:
                    for reason in result.reasons:
                        st.markdown(f"- {reason}")
                else:
                    st.markdown("- Aucun pour le moment")

            with col2:
                st.markdown("**⚠️ Points d'attention:**")
                if result.warnings:
                    for warning in result.warnings:
                        st.markdown(f"- {warning}")
                else:
                    st.markdown("- Aucun identifié")

            if result.signal_detected:
                st.markdown("---")
                st.markdown("**📐 Niveaux techniques indicatifs:**")

                # Visual representation
                if result.entry_level and result.invalidation_level and result.target_level:
                    entry = result.entry_level
                    stop = result.invalidation_level
                    target = result.target_level

                    risk_pct = abs((stop - entry) / entry * 100)
                    reward_pct = abs((target - entry) / entry * 100)

                    cols = st.columns(4)
                    cols[0].metric("🎯 Entrée", f"{entry:.2f}")
                    cols[1].metric("🛑 Stop", f"{stop:.2f}", f"-{risk_pct:.1f}%", delta_color="inverse")
                    cols[2].metric("🎁 Objectif", f"{target:.2f}", f"+{reward_pct:.1f}%")
                    cols[3].metric("⚖️ R/R", f"{result.risk_reward_ratio:.2f}")

                    # Visual bar
                    st.markdown("**Visualisation:**")
                    st.markdown(f"""
                    ```
                    🛑 Stop: {stop:.2f} ◄────────┤ RISQUE: -{risk_pct:.1f}%
                                                │
                    🎯 Entrée: {entry:.2f}      ┼ ◄── Vous êtes ici
                                                │
                    🎁 Objectif: {target:.2f}   ┤ GAIN: +{reward_pct:.1f}%
                    ```
                    """)


def render_risk_disclaimer() -> None:
    """Render risk disclaimer banner."""
    st.warning(
        """
        ⚠️ **Avertissement Important**

        Cette application fournit uniquement une **analyse technique** à des fins éducatives et personnelles.
        Elle ne constitue en aucun cas un conseil en investissement.

        - Les signaux détectés sont purement indicatifs
        - Les niveaux techniques sont des repères théoriques
        - Toute décision d'investissement reste de votre entière responsabilité
        - Les performances passées ne préjugent pas des performances futures
        """
    )
