"""
Stock Analyzer - Main Streamlit Application.

Launch with: streamlit run app/main.py
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from typing import Dict, List
from loguru import logger

from config.settings import get_settings
from src.utils.helpers import load_tickers, setup_logging, get_available_watchlists
from src.data.downloader import download_all_tickers, preload_ticker_info
from src.data.cache import CacheManager
from src.indicators.technical import calculate_indicators
from src.scoring.scorer import SignalScorer, TickerAnalysis
from app.components.dashboard import render_dashboard


# Page configuration
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 5px;
    }
    .stDataFrame {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "data" not in st.session_state:
        st.session_state["data"] = {}
    if "analyses" not in st.session_state:
        st.session_state["analyses"] = []
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = None
    if "data_loaded" not in st.session_state:
        st.session_state["data_loaded"] = False


def load_and_analyze_data(tickers: List[str], force_refresh: bool = False) -> tuple:
    """
    Load data and run analysis.

    Args:
        tickers: List of ticker symbols
        force_refresh: Force data refresh

    Returns:
        Tuple of (data dict, analyses list)
    """
    settings = get_settings()

    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Download data
    status_text.text("Téléchargement des données...")

    def download_progress(ticker, current, total):
        progress_bar.progress(current / total * 0.5)
        status_text.text(f"Téléchargement: {ticker} ({current}/{total})")

    data, failed = download_all_tickers(
        tickers,
        use_cache=True,
        force_refresh=force_refresh,
        progress_callback=download_progress
    )

    if failed:
        st.warning(f"Échec du téléchargement pour: {', '.join(failed)}")

    # Preload company names
    status_text.text("Récupération des noms d'entreprises...")
    progress_bar.progress(0.55)
    preload_ticker_info(list(data.keys()))

    # Calculate indicators
    status_text.text("Calcul des indicateurs...")
    progress_bar.progress(0.6)

    for ticker, df in data.items():
        data[ticker] = calculate_indicators(df)

    # Run analysis
    status_text.text("Analyse des signaux...")
    progress_bar.progress(0.8)

    scorer = SignalScorer()
    analyses = scorer.analyze_watchlist(data)

    progress_bar.progress(1.0)
    status_text.text("Analyse terminée!")

    return data, analyses


def render_sidebar():
    """Render sidebar with controls."""
    settings = get_settings()

    st.sidebar.title("📊 Stock Analyzer")
    st.sidebar.markdown("---")

    # Data loading section
    st.sidebar.header("📁 Données")

    # Get available watchlists
    available_watchlists = get_available_watchlists()

    # Watchlist selector
    if available_watchlists:
        watchlist_names = list(available_watchlists.keys())

        # Initialize session state for watchlist if not exists
        if "selected_watchlist_name" not in st.session_state:
            st.session_state["selected_watchlist_name"] = watchlist_names[0]

        selected_watchlist_name = st.sidebar.selectbox(
            "🎯 Choisir une watchlist",
            options=watchlist_names,
            index=watchlist_names.index(st.session_state["selected_watchlist_name"])
                  if st.session_state["selected_watchlist_name"] in watchlist_names else 0,
            help="🎯 Sélectionnez une watchlist thématique prédéfinie pour analyser un secteur spécifique"
        )

        # Update session state
        st.session_state["selected_watchlist_name"] = selected_watchlist_name
        tickers_file = str(available_watchlists[selected_watchlist_name])

        # Show number of tickers in selected watchlist
        try:
            tickers_count = len(load_tickers(Path(tickers_file)))
            st.sidebar.info(f"📊 {tickers_count} tickers dans cette liste")
        except:
            pass
    else:
        # Fallback to manual input if no watchlists found
        tickers_file = st.sidebar.text_input(
            "Fichier tickers",
            value=str(settings.tickers_file),
            help="📄 Chemin vers un fichier contenant la liste des tickers à analyser (un ticker par ligne). Ex: tickers.txt"
        )

    # Expandable section for manual ticker input
    with st.sidebar.expander("✍️ Saisie manuelle (optionnel)", expanded=False):
        manual_tickers = st.text_area(
            "Tickers personnalisés (un par ligne)",
            placeholder="AAPL\nMSFT\nGOOGL",
            height=100,
            help="✍️ Saisissez manuellement les symboles boursiers à analyser. Cette méthode a priorité sur le fichier.",
            key="manual_tickers_input"
        )

    # Force refresh option
    force_refresh = st.sidebar.checkbox(
        "Forcer le rafraîchissement",
        value=False,
        help="🔄 Force le re-téléchargement des données même si elles sont en cache. Utile pour obtenir les dernières données du marché."
    )

    # Load button
    if st.sidebar.button("🔄 Charger / Actualiser", type="primary"):
        # Get tickers
        tickers = []

        # Check if using manual input
        manual_input = st.session_state.get("manual_tickers_input", "")
        if manual_input and manual_input.strip():
            tickers = [t.strip().upper() for t in manual_input.strip().split("\n") if t.strip()]
            st.sidebar.info(f"Mode: Saisie manuelle ({len(tickers)} tickers)")
        else:
            try:
                tickers = load_tickers(Path(tickers_file))
                st.sidebar.info(f"Mode: {selected_watchlist_name}")
            except FileNotFoundError:
                st.sidebar.error(f"Fichier non trouvé: {tickers_file}")
                return

        if not tickers:
            st.sidebar.error("Aucun ticker à analyser")
            return

        st.sidebar.success(f"✅ {len(tickers)} tickers à analyser")

        # Load and analyze
        with st.spinner("Analyse en cours..."):
            data, analyses = load_and_analyze_data(tickers, force_refresh)

        st.session_state["data"] = data
        st.session_state["analyses"] = analyses
        st.session_state["data_loaded"] = True
        st.session_state["current_watchlist"] = selected_watchlist_name
        st.rerun()

    # Cache info
    st.sidebar.markdown("---")
    st.sidebar.header("💾 Cache")

    cache = CacheManager()
    cache_info = cache.get_cache_info()

    st.sidebar.text(f"Tickers en cache: {cache_info['num_tickers']}")
    st.sidebar.text(f"Taille: {cache_info['total_size_mb']:.2f} MB")

    if st.sidebar.button("🗑️ Vider le cache"):
        cache.clear_cache()
        st.sidebar.success("Cache vidé")

    # Navigation hint
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Navigation")
    st.sidebar.markdown("""
    Utilisez les pages dans la barre latérale:
    - 🏆 **Top Selections**: Meilleurs actions par critères
    - 📈 **Backtesting**: Tester les stratégies
    - 🔔 **Alertes**: Configurer les notifications
    """)


def auto_preload_data():
    """
    Automatically preload a small watchlist if cache is empty and no data loaded.

    Returns:
        True if data was preloaded, False otherwise
    """
    # Skip if data already loaded
    if st.session_state.get("data_loaded", False):
        return False

    # Skip if auto-preload already attempted this session
    if st.session_state.get("auto_preload_attempted", False):
        return False

    # Mark that we've attempted auto-preload
    st.session_state["auto_preload_attempted"] = True

    # Check if cache is empty
    cache = CacheManager()
    cache_info = cache.get_cache_info()

    # Only auto-load if cache is completely empty
    if cache_info['num_tickers'] == 0:
        # Small list of popular, liquid stocks for initial demo
        default_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN"]

        st.info("🚀 Premier démarrage détecté ! Chargement d'une liste d'exemple...")

        with st.spinner("Préchargement des données..."):
            try:
                data, analyses = load_and_analyze_data(default_tickers)
                st.session_state["data"] = data
                st.session_state["analyses"] = analyses
                st.session_state["data_loaded"] = True
                st.session_state["current_watchlist"] = "Exemple (Tech Leaders)"
                st.success(f"✅ {len(data)} actions chargées ! Vous pouvez maintenant charger votre propre liste.")
                return True
            except Exception as e:
                logger.error(f"Auto-preload failed: {e}")
                st.warning("⚠️ Le préchargement automatique a échoué. Chargez manuellement vos tickers.")
                return False

    return False


def main():
    """Main application entry point - Dashboard page."""
    # Initialize
    setup_logging()
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Auto-preload data on first run if cache is empty
    if auto_preload_data():
        st.rerun()

    # Main content
    if not st.session_state["data_loaded"]:
        # Welcome screen
        st.title("📊 Stock Analyzer - Tableau de bord")
        st.markdown("""
        ## Bienvenue!

        Cette application analyse votre watchlist et détecte des **setups techniques** prédéfinis.

        ### 🎯 6 Stratégies détectées:
        1. **Trend Pullback**: Repli vers SMA50 dans une tendance haussière
        2. **Breakout**: Cassure des plus hauts avec volume
        3. **Mean Reversion**: Rebond depuis zone de survente (BB + RSI)
        4. **MACD Crossover**: Changement de momentum (croisement MACD)
        5. **Golden Cross**: SMA50 croise SMA200 (signal long terme)
        6. **Volume Breakout**: Cassure avec explosion de volume

        ### 📖 Pour commencer:
        1. Créez un fichier `tickers.txt` avec un ticker par ligne
        2. Ou saisissez vos tickers directement dans la barre latérale
        3. Cliquez sur **🔄 Charger / Actualiser**
        4. Explorez les pages dans la sidebar:
           - 🏆 **Top Selections**: Meilleurs actions par critères
           - 📈 **Backtesting**: Tester les stratégies historiquement
           - 🔔 **Alertes**: Configurer les notifications

        ---

        ⚠️ **Avertissement**: Cette application fournit uniquement une analyse technique
        à des fins éducatives. Elle ne constitue pas un conseil en investissement.
        """)

        # Quick start with example tickers
        st.subheader("🚀 Démarrage rapide")
        if st.button("Analyser des tickers exemple (AAPL, MSFT, GOOGL, AMZN, NVDA)"):
            example_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
            with st.spinner("Analyse en cours..."):
                data, analyses = load_and_analyze_data(example_tickers)
            st.session_state["data"] = data
            st.session_state["analyses"] = analyses
            st.session_state["data_loaded"] = True
            st.rerun()

    else:
        # Render dashboard
        render_dashboard(
            st.session_state["analyses"],
            st.session_state["data"]
        )


if __name__ == "__main__":
    main()
