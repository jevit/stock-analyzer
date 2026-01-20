"""
Top Picks page - Best stocks by various criteria.
"""
import streamlit as st
import pandas as pd
from typing import List

from src.analysis.rankings import TopRankings, RankedStock
from src.analysis.fundamentals import get_all_fundamentals


def render_top_table(stocks: List[RankedStock], show_tech_score: bool = True, key_prefix: str = "") -> None:
    """
    Render a ranked stock table.

    Args:
        stocks: List of RankedStock
        show_tech_score: Show technical score column
        key_prefix: Unique prefix for button keys to avoid duplicates
    """
    if not stocks:
        st.info("Aucune action ne correspond aux critères")
        return

    # Build DataFrame
    data = []
    for stock in stocks:
        row = {
            "🏆": f"#{stock.rank}",
            "Ticker": stock.ticker,
            "Nom": stock.name[:25] + "..." if len(stock.name) > 25 else stock.name,
            "Prix": f"{stock.price:.2f}",
        }

        if show_tech_score:
            row["Tech"] = stock.technical_score

        # Add specific metrics
        if stock.metric1_label:
            row[stock.metric1_label] = stock.metric1_value
        if stock.metric2_label:
            row[stock.metric2_label] = stock.metric2_value
        if stock.metric3_label:
            row[stock.metric3_label] = stock.metric3_value

        data.append(row)

    df = pd.DataFrame(data)

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # Details in expander
    with st.expander("📋 Détails des sélections"):
        for stock in stocks:
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                st.markdown(f"**#{stock.rank}**")

            with col2:
                st.markdown(f"**{stock.ticker}** - {stock.name}")

            with col3:
                if st.button(f"Voir détails →", key=f"{key_prefix}_detail_{stock.ticker}"):
                    st.session_state["selected_ticker"] = stock.ticker
                    st.switch_page("pages/4_Detail.py")

            st.caption(stock.reason)
            st.markdown("---")


def render_top_picks_page():
    """Render the top picks page."""
    st.title("🏆 Top Sélections")

    st.markdown("""
    Découvrez les meilleures actions selon différents critères d'investissement.
    """)

    # Check if data is loaded
    if not st.session_state.get("data_loaded"):
        st.warning("⚠️ Chargez d'abord des données depuis le tableau de bord")
        if st.button("📊 Aller au tableau de bord"):
            st.switch_page("main.py")
        return

    # Get analyses and data
    analyses = st.session_state.get("analyses", [])
    data = st.session_state.get("data", {})

    if not analyses:
        st.error("Aucune analyse disponible")
        return

    # Check if fundamentals are cached
    if "fundamentals" not in st.session_state:
        with st.spinner("Récupération des données fondamentales..."):
            fundamentals = get_all_fundamentals(data)
            st.session_state["fundamentals"] = fundamentals
    else:
        fundamentals = st.session_state["fundamentals"]

    # Create rankings
    rankings = TopRankings(analyses, fundamentals, data)

    # Settings
    with st.sidebar:
        st.header("⚙️ Paramètres")
        top_n = st.slider(
            "Nombre d'actions",
            min_value=5,
            max_value=20,
            value=10,
            help="📊 Nombre d'actions à afficher dans chaque classement. Plus le nombre est élevé, plus vous verrez d'opportunités potentielles."
        )

    # Tabs for different criteria
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Technique",
        "🚀 Momentum",
        "💎 Value",
        "📈 Growth",
        "💰 Dividendes",
        "⭐ Qualité",
        "🛡️ Défensif"
    ])

    with tab1:
        st.header("📊 Top Technique")
        st.markdown("""
        Actions avec les **meilleurs scores techniques** : signaux forts, indicateurs positifs, setups validés.

        **Idéal pour** : Trading court/moyen terme, suivre les signaux techniques
        """)

        with st.spinner("Calcul du top technique..."):
            top_tech = rankings.get_top_technical(top_n)
            render_top_table(top_tech, show_tech_score=True, key_prefix="tech")

    with tab2:
        st.header("🚀 Top Momentum")
        st.markdown("""
        Actions avec la **plus forte dynamique haussière** : performances récentes élevées, tendance forte.

        **Idéal pour** : Surfer sur la tendance, investissement momentum
        """)

        with st.spinner("Calcul du top momentum..."):
            top_momentum = rankings.get_top_momentum(top_n)
            render_top_table(top_momentum, show_tech_score=False, key_prefix="momentum")

    with tab3:
        st.header("💎 Top Value")
        st.markdown("""
        Actions **sous-évaluées** : P/E faible, P/B attractif, fondamentaux solides à prix raisonnable.

        **Idéal pour** : Value investing, vision long terme, recherche de décote
        """)

        with st.spinner("Calcul du top value..."):
            top_value = rankings.get_top_value(top_n)
            render_top_table(top_value, show_tech_score=False, key_prefix="value")

    with tab4:
        st.header("📈 Top Growth")
        st.markdown("""
        Actions à **forte croissance** : revenus et bénéfices en expansion, potentiel élevé.

        **Idéal pour** : Croissance long terme, secteurs innovants
        """)

        with st.spinner("Calcul du top growth..."):
            top_growth = rankings.get_top_growth(top_n)
            render_top_table(top_growth, show_tech_score=False, key_prefix="growth")

    with tab5:
        st.header("💰 Top Dividendes")
        st.markdown("""
        Actions avec les **meilleurs dividendes** : rendement élevé, payout soutenable.

        **Idéal pour** : Revenus passifs, investissement défensif
        """)

        with st.spinner("Calcul du top dividendes..."):
            top_div = rankings.get_top_dividend(top_n)
            render_top_table(top_div, show_tech_score=False, key_prefix="dividend")

    with tab6:
        st.header("⭐ Top Qualité")
        st.markdown("""
        Actions de **haute qualité** : ROE élevé, marges importantes, fondamentaux solides.

        **Idéal pour** : Investissement de qualité, entreprises leaders
        """)

        with st.spinner("Calcul du top qualité..."):
            top_quality = rankings.get_top_quality(top_n)
            render_top_table(top_quality, show_tech_score=False, key_prefix="quality")

    with tab7:
        st.header("🛡️ Top Défensif")
        st.markdown("""
        Actions **peu volatiles** : faible risque, stabilité, dividendes possibles.

        **Idéal pour** : Préservation du capital, profil conservateur
        """)

        with st.spinner("Calcul du top défensif..."):
            top_def = rankings.get_top_defensive(top_n)
            render_top_table(top_def, show_tech_score=False, key_prefix="defensive")

    # Disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **Avertissement**: Ces classements sont basés sur des critères techniques et fondamentaux automatiques.
    Ils ne constituent pas des recommandations d'investissement. Faites toujours vos propres recherches.
    """)
