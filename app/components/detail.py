"""
Detail page - Individual ticker analysis.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional

from src.scoring.scorer import TickerAnalysis
from app.components.charts import create_price_chart, create_indicator_chart
from app.components.tables import (
    render_strategy_details,
    render_risk_disclaimer,
    render_novice_summary,
    render_indicator_legend,
)
from app.utils.tooltips import TOOLTIPS
from app.components.metrics import metric_with_tooltip


def render_global_verdict(analysis: TickerAnalysis) -> None:
    """
    Render the global verdict card prominently.

    Args:
        analysis: TickerAnalysis object
    """
    st.markdown("## 🎯 Verdict Global")

    # Main verdict box with color based on score
    if analysis.global_score >= 80:
        box_color = "rgba(27, 94, 32, 0.3)"  # Green
        border_color = "#4caf50"
    elif analysis.global_score >= 60:
        box_color = "rgba(51, 105, 30, 0.3)"  # Light green
        border_color = "#8bc34a"
    elif analysis.global_score >= 40:
        box_color = "rgba(130, 119, 23, 0.3)"  # Yellow
        border_color = "#ffc107"
    else:
        box_color = "rgba(74, 74, 74, 0.3)"  # Gray
        border_color = "#9e9e9e"

    # Display verdict in a prominent box
    st.markdown(f"""
    <div style="
        background-color: {box_color};
        border-left: 5px solid {border_color};
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    ">
        <h2 style="margin: 0; color: white;">{analysis.verdict_emoji} {analysis.verdict}</h2>
        <p style="font-size: 1.2em; margin: 10px 0; color: #e0e0e0;">
            Score: <strong>{analysis.global_score}/100</strong>
            {f"| Stratégie: <strong>{analysis.best_strategy}</strong>" if analysis.best_strategy else ""}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Action suggestion in a callout
    if analysis.action_suggestion:
        if "priorité" in analysis.action_suggestion.lower() or "étudier" in analysis.action_suggestion.lower():
            st.success(f"**Suggestion:** {analysis.action_suggestion}")
        elif "surveiller" in analysis.action_suggestion.lower():
            st.info(f"**Suggestion:** {analysis.action_suggestion}")
        elif "patienter" in analysis.action_suggestion.lower() or "attendre" in analysis.action_suggestion.lower():
            st.warning(f"**Suggestion:** {analysis.action_suggestion}")
        else:
            st.info(f"**Suggestion:** {analysis.action_suggestion}")

    # Detailed verdict explanation
    with st.expander("📖 Explication détaillée du verdict", expanded=True):
        st.markdown(analysis.verdict_detail)

        # Final disclaimer
        st.markdown("---")
        st.markdown("""
        <div style="
            background-color: rgba(255, 152, 0, 0.2);
            border-left: 4px solid #ff9800;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        ">
            <strong>⚠️ Rappel Important</strong><br>
            Ce verdict est une <strong>analyse technique automatique</strong> basée sur des indicateurs mathématiques.
            Il ne constitue <strong>PAS un conseil d'investissement</strong>.<br><br>
            • L'analyse technique a ses limites et ne prédit pas l'avenir<br>
            • Les conditions de marché peuvent changer rapidement<br>
            • Faites toujours vos propres recherches (fondamentaux, actualités, etc.)<br>
            • N'investissez que ce que vous pouvez vous permettre de perdre
        </div>
        """, unsafe_allow_html=True)


def render_detail_page(
    ticker: str,
    analysis: Optional[TickerAnalysis],
    df: Optional[pd.DataFrame]
) -> None:
    """
    Render detailed analysis for a single ticker.

    Args:
        ticker: Ticker symbol
        analysis: TickerAnalysis object
        df: Price DataFrame with indicators
    """
    # Back button
    if st.button("← Retour au tableau de bord"):
        st.switch_page("main.py")

    # Display title with company name if available
    if analysis and analysis.name and analysis.name != ticker:
        st.title(f"📈 {analysis.name}")
        st.markdown(f"**Ticker:** `{ticker}`")
    else:
        st.title(f"📈 Analyse détaillée: {ticker}")

    if analysis is None or df is None:
        st.error(f"Données non disponibles pour {ticker}")
        return

    # Render disclaimer (collapsed)
    with st.expander("⚠️ Avertissement", expanded=False):
        render_risk_disclaimer()

    # ========== GLOBAL VERDICT SECTION ==========
    st.markdown("---")
    render_global_verdict(analysis)

    # ========== NOVICE SUMMARY SECTION ==========
    st.markdown("---")
    render_novice_summary(analysis)

    # ========== QUICK METRICS ==========
    st.markdown("---")
    st.subheader("📊 Métriques clés")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        score_delta = None
        score_color = "off"
        if analysis.global_score >= 75:
            score_delta = "Fort"
            score_color = "normal"
        elif analysis.global_score >= 50:
            score_delta = "Moyen"
        metric_with_tooltip(
            "🎯 Score Global",
            f"{analysis.global_score}/100",
            tooltip_key="SCORE",
            delta=score_delta,
            delta_color=score_color
        )

    with col2:
        metric_with_tooltip(
            "💰 Prix",
            f"{analysis.close:.2f}",
            help_text="Prix de clôture actuel de l'action"
        )

    with col3:
        change_color = "normal" if analysis.change_1d_pct >= 0 else "inverse"
        metric_with_tooltip(
            "📅 Variation 1J",
            f"{analysis.change_1d_pct:+.2f}%",
            help_text="Variation du prix sur la dernière journée de trading. Une variation positive (verte) indique une hausse, négative (rouge) une baisse.",
            delta=f"{analysis.change_1d_pct:+.2f}%",
            delta_color=change_color
        )

    with col4:
        rsi_val = analysis.rsi if analysis.rsi else 0
        rsi_status = None
        if rsi_val > 70:
            rsi_status = "Surachat ⚠️"
        elif rsi_val < 30:
            rsi_status = "Survente 💡"
        metric_with_tooltip(
            "⚡ RSI",
            f"{rsi_val:.1f}",
            tooltip_key="RSI",
            delta=rsi_status
        )

    with col5:
        atr_val = analysis.atr_pct if analysis.atr_pct else 0
        vol_status = None
        if atr_val > 4:
            vol_status = "Élevée ⚠️"
        elif atr_val < 1.5:
            vol_status = "Faible"
        metric_with_tooltip(
            "🎢 Volatilité",
            f"{atr_val:.2f}%",
            tooltip_key="ATR_PCT",
            delta=vol_status
        )

    # ========== SIGNAL & LEVELS ==========
    if analysis.has_signal:
        st.markdown("---")
        st.success(f"✅ **Signal détecté**: {analysis.best_strategy}")

        st.subheader("📐 Niveaux Techniques (Indicatifs)")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if analysis.entry_level:
                metric_with_tooltip(
                    "🎯 Entrée théorique",
                    f"{analysis.entry_level:.2f}",
                    tooltip_key="ENTRY"
                )

        with col2:
            if analysis.invalidation_level:
                invalidation_pct = ((analysis.invalidation_level - analysis.close) / analysis.close) * 100
                metric_with_tooltip(
                    "🛑 Invalidation",
                    f"{analysis.invalidation_level:.2f}",
                    tooltip_key="STOP_LOSS",
                    delta=f"{invalidation_pct:.1f}%",
                    delta_color="inverse"
                )

        with col3:
            if analysis.target_level:
                target_pct = ((analysis.target_level - analysis.close) / analysis.close) * 100
                metric_with_tooltip(
                    "🎁 Objectif",
                    f"{analysis.target_level:.2f}",
                    tooltip_key="TAKE_PROFIT",
                    delta=f"+{target_pct:.1f}%"
                )

        with col4:
            if analysis.risk_reward_ratio:
                metric_with_tooltip(
                    "⚖️ Ratio R/R",
                    f"{analysis.risk_reward_ratio:.2f}",
                    tooltip_key="RR"
                )

        # Visual explanation of levels
        if analysis.entry_level and analysis.invalidation_level and analysis.target_level:
            with st.expander("📖 Comment lire ces niveaux?", expanded=False):
                entry = analysis.entry_level
                stop = analysis.invalidation_level
                target = analysis.target_level
                risk_pct = abs((stop - entry) / entry * 100)
                reward_pct = abs((target - entry) / entry * 100)

                rr_text = ""
                if analysis.risk_reward_ratio:
                    rr_text = f"""
                - **⚖️ Ratio R/R = {analysis.risk_reward_ratio:.2f}**
                  → Pour chaque euro risqué, vous pouvez potentiellement en gagner {analysis.risk_reward_ratio:.1f}
"""

                st.markdown(f"""
                ### Explication simple

                Imaginez que vous entrez à **{entry:.2f}** :

                - **🛑 Si ça baisse** jusqu'à {stop:.2f} (-{risk_pct:.1f}%), le setup est invalidé
                  → C'est votre "niveau de protection"

                - **🎁 Si ça monte** jusqu'à {target:.2f} (+{reward_pct:.1f}%), l'objectif est atteint
                  → C'est votre "niveau de prise de profit"
{rr_text}

                ```
                🎁 Objectif    {target:.2f}  ──────  +{reward_pct:.1f}% (gain potentiel)
                               │
                               │
                🎯 Entrée      {entry:.2f}  ══════  ◄── Vous êtes ici
                               │
                               │
                🛑 Stop        {stop:.2f}  ──────  -{risk_pct:.1f}% (risque maximum)
                ```

                ⚠️ **Rappel**: Ces niveaux sont calculés automatiquement (basés sur 2x ATR).
                Ce sont des repères, pas des recommandations!
                """)

    else:
        st.info("ℹ️ **Aucun signal détecté** pour ce ticker. Les conditions des stratégies surveillées ne sont pas réunies.")

    # ========== CHARTS ==========
    st.markdown("---")
    st.subheader("📈 Graphiques")

    # Chart options in expander
    with st.expander("⚙️ Options du graphique", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            days = st.selectbox("Période", [60, 90, 180, 365], index=2)
        with col2:
            show_sma = st.checkbox("Afficher SMAs", value=True)
        with col3:
            show_bb = st.checkbox("Afficher Bollinger", value=True)
        with col4:
            show_volume = st.checkbox("Afficher Volume", value=True)

    # Price chart
    price_chart = create_price_chart(
        df,
        ticker,
        show_sma=show_sma,
        show_bb=show_bb,
        show_volume=show_volume,
        days=days,
    )
    st.plotly_chart(price_chart, use_container_width=True)

    # Chart legend for novices
    with st.expander("📖 Comment lire ce graphique?", expanded=False):
        st.markdown("""
        ### Guide de lecture du graphique

        **Les bougies (chandeliers):**
        - 🟢 **Bougie verte** = Le prix a monté ce jour-là
        - 🔴 **Bougie rouge** = Le prix a baissé ce jour-là
        - La hauteur montre l'amplitude du mouvement

        **Les lignes de couleur (Moyennes Mobiles):**
        - 🔵 **Ligne bleue (SMA20)** = Tendance court terme (20 jours)
        - 🟠 **Ligne orange (SMA50)** = Tendance moyen terme (50 jours)
        - 🟣 **Ligne violette (SMA200)** = Tendance long terme (200 jours)

        **Règle simple:**
        - Prix AU-DESSUS des lignes = Tendance haussière ✅
        - Prix EN DESSOUS des lignes = Tendance baissière ⚠️

        **Les bandes grises (Bollinger):**
        - Bande haute = Zone de "surachat" potentiel
        - Bande basse = Zone de "survente" potentiel
        - Le prix oscille généralement entre ces bandes

        **Le volume (barres en bas):**
        - Barres hautes = Beaucoup d'activité (intérêt fort)
        - Barres basses = Peu d'activité
        - La ligne orange = Volume moyen (référence)
        """)

    # Indicator chart
    st.subheader("📉 Indicateurs techniques")
    indicator_chart = create_indicator_chart(df, days=days)
    st.plotly_chart(indicator_chart, use_container_width=True)

    # Indicator legend
    with st.expander("📖 Comment lire ces indicateurs?", expanded=False):
        st.markdown("""
        ### RSI (Relative Strength Index)

        Le RSI mesure si une action monte ou descend "trop vite":

        - **Zone rouge (>70)**: L'action est en "surachat"
          → Elle a beaucoup monté, elle pourrait faire une pause

        - **Zone verte (<30)**: L'action est en "survente"
          → Elle a beaucoup baissé, elle pourrait rebondir

        - **Ligne à 50**: Le milieu, zone neutre

        ### ATR% (Volatilité)

        L'ATR% montre combien l'action bouge en moyenne par jour:

        - **>5%**: Très volatile (gros mouvements, plus risqué)
        - **2-5%**: Volatile (mouvements significatifs)
        - **<2%**: Calme (petits mouvements)
        """)

    # ========== STRATEGY DETAILS ==========
    st.markdown("---")
    render_strategy_details(analysis)

    # ========== RISK ANALYSIS ==========
    st.markdown("---")
    st.subheader("⚠️ Analyse des Risques")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Points positifs")
        if analysis.reasons:
            for reason in analysis.reasons[:7]:
                st.markdown(f"- {reason}")
        else:
            st.markdown("- Aucun point positif majeur identifié")

    with col2:
        st.markdown("### ⚠️ Points d'attention")
        if analysis.warnings:
            for warning in analysis.warnings[:7]:
                st.markdown(f"- {warning}")
        else:
            st.markdown("- Aucun point d'attention majeur")

    # Risk summary box
    if analysis.risk_summary:
        st.warning(f"**🚨 Synthèse des risques:** {analysis.risk_summary}")

    # ========== RAW DATA ==========
    with st.expander("📋 Données brutes (derniers jours)"):
        cols_to_show = ["Open", "High", "Low", "Close", "Volume"]
        if "RSI" in df.columns:
            cols_to_show.append("RSI")
        if "ATR_pct" in df.columns:
            cols_to_show.append("ATR_pct")

        recent_data = df.tail(10)[cols_to_show].round(2)
        st.dataframe(recent_data, use_container_width=True)
