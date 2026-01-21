"""
Dashboard page - Main opportunities table.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict

from src.scoring.scorer import TickerAnalysis
from app.components.tables import (
    create_opportunities_table,
    create_novice_table,
    style_opportunities_table,
    render_risk_disclaimer,
    render_indicator_legend,
)


def render_filters(analyses: List[TickerAnalysis]) -> Dict:
    """
    Render sidebar filters.

    Args:
        analyses: List of analyses to filter

    Returns:
        Dict with filter values
    """
    st.sidebar.header("🎚️ Filtres")

    # Score filter
    min_score = st.sidebar.slider(
        "Score minimum",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="📊 **Score global** (0-100) : Évaluation combinée de tous les indicateurs techniques. Plus le score est élevé, plus le signal est fort. 80+ = Excellent, 60-79 = Bon, 40-59 = Moyen, <40 = Faible"
    )

    # Strategy filter
    strategies = ["Tous"] + list(set(
        a.best_strategy for a in analyses if a.best_strategy
    ))
    selected_strategy = st.sidebar.selectbox(
        "Stratégie",
        options=strategies,
        help="Filtrer par type de stratégie détectée"
    )

    # Volatility filter
    st.sidebar.markdown("**Volatilité (ATR%)**")
    st.sidebar.caption("📊 ATR% = Average True Range en % du prix. Mesure la volatilité moyenne. <1.5% = Calme, 1.5-3% = Normal, 3-5% = Volatile, >5% = Très risqué")
    col1, col2 = st.sidebar.columns(2)
    min_atr = col1.number_input("Min", value=0.0, step=0.5, key="min_atr", help="Volatilité minimale acceptée")
    max_atr = col2.number_input("Max", value=100.0, step=0.5, key="max_atr", help="Volatilité maximale acceptée")

    # Volume filter
    min_volume_ratio = st.sidebar.number_input(
        "Volume ratio min",
        value=0.0,
        step=0.1,
        help="📊 **Volume Ratio** : Volume du jour divisé par la moyenne des 20 derniers jours. >2x = Très fort intérêt, 1.5-2x = Fort, 0.8-1.5x = Normal, <0.8x = Faible intérêt. Un volume élevé confirme la force du mouvement."
    )

    # Signal only filter
    signal_only = st.sidebar.checkbox(
        "✅ Signaux uniquement",
        value=False,
        help="Afficher uniquement les tickers avec un signal actif"
    )

    return {
        "min_score": min_score,
        "strategy": selected_strategy,
        "min_atr": min_atr,
        "max_atr": max_atr,
        "min_volume_ratio": min_volume_ratio,
        "signal_only": signal_only,
    }


def apply_filters(analyses: List[TickerAnalysis], filters: Dict) -> List[TickerAnalysis]:
    """
    Apply filters to analyses list.

    Args:
        analyses: Original list
        filters: Filter values

    Returns:
        Filtered list
    """
    filtered = analyses.copy()

    # Score filter
    filtered = [a for a in filtered if a.global_score >= filters["min_score"]]

    # Strategy filter
    if filters["strategy"] != "Tous":
        filtered = [a for a in filtered if a.best_strategy == filters["strategy"]]

    # Volatility filter
    filtered = [
        a for a in filtered
        if a.atr_pct is not None and filters["min_atr"] <= a.atr_pct <= filters["max_atr"]
    ]

    # Volume filter
    filtered = [
        a for a in filtered
        if a.volume_ratio is not None and a.volume_ratio >= filters["min_volume_ratio"]
    ]

    # Signal only filter
    if filters["signal_only"]:
        filtered = [a for a in filtered if a.has_signal]

    return filtered


def render_overview_widget(analyses: List[TickerAnalysis]) -> None:
    """Render overview statistics widget."""
    signals_strong = [a for a in analyses if a.has_signal and a.global_score >= 75]
    signals_all = [a for a in analyses if a.has_signal]

    if signals_strong:
        st.markdown("---")
        st.markdown("### 🔥 Signaux Forts du Jour")

        # Top 3 signals
        top_signals = sorted(signals_strong, key=lambda x: x.global_score, reverse=True)[:3]

        for i, a in enumerate(top_signals, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"

            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                st.markdown(f"### {emoji}")

            with col2:
                st.markdown(f"**{a.ticker}** - {a.name}")
                st.caption(f"{a.best_strategy} | Score: {a.global_score}/100")

            with col3:
                if st.button("Voir →", key=f"view_{a.ticker}"):
                    st.session_state["selected_ticker"] = a.ticker
                    st.switch_page("pages/4_Detail.py")

        st.markdown("---")


def render_dashboard(
    analyses: List[TickerAnalysis],
    data: Dict[str, pd.DataFrame]
) -> None:
    """
    Render the main dashboard page.

    Args:
        analyses: List of TickerAnalysis
        data: Dict of ticker DataFrames
    """
    st.title("📊 Stock Analyzer - Tableau de bord")

    # Show current watchlist if available
    if "current_watchlist" in st.session_state and st.session_state["current_watchlist"]:
        st.info(f"📂 Watchlist active: **{st.session_state['current_watchlist']}**")

    # Render disclaimer (collapsed)
    with st.expander("⚠️ Avertissement Important", expanded=False):
        render_risk_disclaimer()

    # Render filters
    filters = render_filters(analyses)
    filtered_analyses = apply_filters(analyses, filters)

    # Display mode selector
    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Affichage")
    display_mode = st.sidebar.radio(
        "Mode d'affichage",
        ["🎓 Débutant (avec explications)", "📊 Expert (compact)"],
        help="Choisir le niveau de détail affiché"
    )
    is_novice_mode = "Débutant" in display_mode

    # Enhanced Stats row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📋 Tickers analysés", len(analyses))

    with col2:
        signals = sum(1 for a in analyses if a.has_signal)
        st.metric("✅ Signaux détectés", signals)

    with col3:
        strong_signals = sum(1 for a in analyses if a.has_signal and a.global_score >= 75)
        st.metric("🔥 Signaux forts", strong_signals, delta=f"Score ≥75" if strong_signals > 0 else None)

    with col4:
        avg_score = sum(a.global_score for a in analyses) / len(analyses) if analyses else 0
        st.metric("📊 Score moyen", f"{avg_score:.0f}")

    with col5:
        # Count new strategies
        new_strat_signals = sum(1 for a in analyses if a.best_strategy in ["MACD Crossover", "Golden Cross", "Volume Breakout"])
        if new_strat_signals > 0:
            st.metric("🆕 Nouvelles strat", new_strat_signals, delta="MACD/Golden/Volume")

    # Overview widget for strong signals
    render_overview_widget(analyses)

    # Legend for novices
    if is_novice_mode:
        render_indicator_legend()

    st.markdown("---")

    # Main table
    st.subheader(f"🎯 Top Opportunités ({len(filtered_analyses)} résultats)")

    if not filtered_analyses:
        st.info("Aucun ticker ne correspond aux filtres sélectionnés.")
        return

    # Create and display table based on mode
    if is_novice_mode:
        st.markdown("*Tableau trié par verdict (du plus favorable au moins favorable) - Survolez les colonnes pour plus d'infos*")
        df = create_novice_table(filtered_analyses, sort_by_verdict=True)

        # Column configuration with tooltips
        column_config = {
            "Ticker": st.column_config.TextColumn(
                "📌 Ticker",
                help="Symbole boursier de l'action",
                width="small",
            ),
            "Nom": st.column_config.TextColumn(
                "🏢 Entreprise",
                help="Nom complet de l'entreprise",
                width="medium",
            ),
            "Verdict": st.column_config.TextColumn(
                "🎯 Verdict",
                help="🌟 FAVORABLE = Signal fort, conditions réunies\n✅ Correct = Signal présent avec réserves\n👀 Surveiller = En développement\n⏸️ Attendre = Pas le bon moment",
                width="medium",
            ),
            "Score": st.column_config.TextColumn(
                "📊 Score",
                help="Score global 0-100 basé sur les 3 stratégies.\n80+ = Excellent | 60-79 = Bon | 40-59 = Moyen | <40 = Faible",
                width="small",
            ),
            "Stratégie": st.column_config.TextColumn(
                "📋 Stratégie",
                help="Type de signal détecté:\n• Trend Pullback = Repli en tendance haussière\n• Breakout = Cassure de résistance\n• Mean Reversion = Rebond de survente",
                width="medium",
            ),
            "Prix": st.column_config.TextColumn(
                "💰 Prix",
                help="Prix de clôture actuel",
                width="small",
            ),
            "Tendance": st.column_config.TextColumn(
                "📈 Tendance",
                help="Position par rapport à la SMA200:\n📈 Haussier = Prix > 5% au-dessus\n↗️ Légèrement + = Prix 0-5% au-dessus\n↘️ Légèrement - = Prix 0-5% en dessous\n📉 Baissier = Prix > 5% en dessous",
                width="medium",
            ),
            "RSI": st.column_config.TextColumn(
                "⚡ RSI",
                help="Momentum (0-100):\n🔴 >70 = Surachat (risque de correction)\n🟢 <30 = Survente (opportunité potentielle)\n🟢 50-70 = Momentum positif\n🟡 30-50 = Momentum faible",
                width="medium",
            ),
            "Volatilité": st.column_config.TextColumn(
                "🎢 Volatilité",
                help="ATR% = mouvement journalier moyen:\n🔴 >5% = Très risqué\n🟡 3-5% = Volatile\n🟢 1.5-3% = Normal\n🔵 <1.5% = Calme",
                width="medium",
            ),
            "Volume": st.column_config.TextColumn(
                "📊 Volume",
                help="Volume vs moyenne 20 jours:\n🟢 >2x = Très fort intérêt\n🟢 1.5-2x = Fort intérêt\n🟡 0.8-1.5x = Normal\n🔴 <0.8x = Faible intérêt",
                width="medium",
            ),
            "Résumé": st.column_config.TextColumn(
                "📝 Résumé",
                help="Résumé rapide de l'analyse avec la raison principale du signal et les risques identifiés",
                width="large",
            ),
        }

        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=min(700, 50 + len(df) * 38),
        )

        # Quick legend reminder
        st.markdown("""
        ---
        **📖 Légende des verdicts:**

        | Verdict | Signification | Action suggérée |
        |---------|--------------|-----------------|
        | 🌟 **FAVORABLE** | Signal fort, conditions réunies | À étudier en priorité |
        | ✅ **Correct** | Signal présent, quelques réserves | Surveiller de près |
        | 👀 **Surveiller** | Setup en développement | Mettre en watchlist |
        | ⏸️ **Attendre** | Conditions non favorables | Patienter |

        *Survolez les en-têtes de colonnes pour plus d'explications*
        """)
    else:
        st.markdown("*Cliquez sur un ticker pour voir les détails*")
        df = create_opportunities_table(filtered_analyses)
        styled_df = style_opportunities_table(df)
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=min(600, 50 + len(df) * 35),
        )

    # Quick summary of top signals
    top_signals = sorted(
        [a for a in filtered_analyses if a.has_signal and a.global_score >= 60],
        key=lambda x: x.global_score,
        reverse=True
    )[:5]
    if top_signals:
        st.markdown("---")
        st.subheader("🏆 Top 5 Signaux du jour")

        for a in top_signals:
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    score_emoji = "🌟" if a.global_score >= 80 else "✅"
                    st.markdown(f"### {score_emoji} {a.ticker}")
                    st.markdown(f"**Score: {a.global_score}/100**")

                with col2:
                    st.markdown(f"**Stratégie:** {a.best_strategy}")
                    st.markdown(f"**Prix:** {a.close:.2f} | **RSI:** {a.rsi:.0f}" if a.rsi else f"**Prix:** {a.close:.2f}")

                    # Quick summary
                    if a.reasons:
                        main_reason = next((r for r in a.reasons if not r.startswith("⭐")), a.reasons[0])
                        st.markdown(f"*{main_reason[:80]}...*" if len(main_reason) > 80 else f"*{main_reason}*")

                with col3:
                    if st.button(f"Voir détail", key=f"btn_{a.ticker}"):
                        st.session_state["selected_ticker"] = a.ticker
                        st.switch_page("pages/4_Detail.py")

                st.markdown("---")

    # Export section
    st.subheader("📥 Export des données")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # Full export
        full_df = create_opportunities_table(
            filtered_analyses,
            show_columns=[
                "Ticker", "Score", "Stratégie", "Prix", "Var. 1J %",
                "RSI", "ATR %", "Vol. Ratio", "Dist. SMA200 %",
                "Entrée", "Invalidation", "Objectif", "R/R", "Signal"
            ]
        )
        csv = full_df.to_csv(index=False)
        st.download_button(
            "📥 Exporter tout (CSV)",
            csv,
            "stock_analysis.csv",
            "text/csv",
        )

    with col2:
        # Signals only export
        signals_df = create_opportunities_table(
            [a for a in filtered_analyses if a.has_signal],
            show_columns=[
                "Ticker", "Score", "Stratégie", "Prix",
                "Entrée", "Invalidation", "Objectif", "R/R"
            ]
        )
        if not signals_df.empty:
            csv_signals = signals_df.to_csv(index=False)
            st.download_button(
                "📥 Exporter signaux",
                csv_signals,
                "signals.csv",
                "text/csv",
            )

    # Ticker selector for detail view
    st.markdown("---")
    st.subheader("🔍 Analyse détaillée d'un ticker")

    ticker_options = [a.ticker for a in filtered_analyses]
    if ticker_options:
        col1, col2 = st.columns([3, 1])

        with col1:
            selected_ticker = st.selectbox(
                "Sélectionner un ticker",
                options=ticker_options,
                format_func=lambda x: f"{x} - Score: {next((a.global_score for a in filtered_analyses if a.ticker == x), 0)} - {next((a.best_strategy for a in filtered_analyses if a.ticker == x), 'N/A')}"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔎 Voir l'analyse", type="primary"):
                st.session_state["selected_ticker"] = selected_ticker
                st.switch_page("pages/4_Detail.py")
