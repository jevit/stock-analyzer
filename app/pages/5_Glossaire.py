"""
Glossaire page - Streamlit multipage.
Explications détaillées de tous les termes techniques.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.components.glossaire import render_glossaire

# Page config
st.set_page_config(
    page_title="Glossaire",
    page_icon="📚",
    layout="wide",
)

# Render the glossaire
render_glossaire()
