"""
Top Selections page - Streamlit multipage.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.components.top_picks import render_top_picks_page

# Page config (optional per-page settings)
st.set_page_config(
    page_title="Top Sélections",
    page_icon="🏆",
    layout="wide",
)

# Render the page
render_top_picks_page()
