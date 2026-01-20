"""
Detail page - Streamlit multipage.
Shows detailed analysis for a selected ticker.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.components.detail import render_detail_page

# Page config
st.set_page_config(
    page_title="Détail Ticker",
    page_icon="🔍",
    layout="wide",
)

# Get selected ticker from session state
ticker = st.session_state.get("selected_ticker")

if not ticker:
    st.warning("⚠️ Aucun ticker sélectionné")
    st.info("Retournez au tableau de bord et cliquez sur un ticker pour voir ses détails.")

    if st.button("📊 Aller au tableau de bord"):
        # Navigate to main page
        st.switch_page("main.py")
else:
    # Get analysis and data from session state
    analysis = next(
        (a for a in st.session_state.get("analyses", []) if a.ticker == ticker),
        None
    )
    df = st.session_state.get("data", {}).get(ticker)

    if analysis and df is not None:
        render_detail_page(ticker, analysis, df)
    else:
        st.error(f"Données non disponibles pour {ticker}")
        if st.button("📊 Retour au tableau de bord"):
            st.switch_page("main.py")
