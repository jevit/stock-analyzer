"""
Glossaire interactif des termes techniques.
"""
import streamlit as st
from app.utils.tooltips import TOOLTIPS


def render_glossaire():
    """Affiche un glossaire interactif des termes techniques."""

    st.title("📚 Glossaire des termes techniques")

    st.markdown("""
    Retrouvez ici toutes les explications des indicateurs et stratégies utilisés dans l'application.
    Cliquez sur une catégorie pour voir les définitions.
    """)

    # Organiser les tooltips par catégories
    categories = {
        "📈 Moyennes Mobiles": ["SMA20", "SMA50", "SMA200"],
        "⚡ Indicateurs de Momentum": ["RSI", "MACD"],
        "🎢 Volatilité": ["ATR", "ATR_PCT", "BB"],
        "📊 Volume": ["VOLUME"],
        "🎯 Score & Niveaux": ["SCORE", "RR", "ENTRY", "STOP_LOSS", "TAKE_PROFIT"],
        "🎯 Stratégies de Trading": [
            "TREND_PULLBACK",
            "BREAKOUT",
            "MEAN_REVERSION",
            "MACD_CROSSOVER",
            "GOLDEN_CROSS",
            "VOLUME_BREAKOUT"
        ]
    }

    # Afficher chaque catégorie dans un expander
    for category, keys in categories.items():
        with st.expander(category, expanded=False):
            for key in keys:
                if key in TOOLTIPS:
                    # Extraire le nom propre du tooltip (première ligne généralement)
                    tooltip_text = TOOLTIPS[key]
                    lines = tooltip_text.split('\n')
                    titre = lines[0].strip() if lines else key

                    st.markdown(f"### {titre}")
                    st.markdown(tooltip_text)
                    st.markdown("---")

    # Section aide rapide
    st.markdown("---")
    st.subheader("💡 Aide rapide")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Comment lire un signal?**

        1. **Score** : Plus il est élevé, mieux c'est
        2. **Stratégie** : Le type d'opportunité détectée
        3. **Niveaux** : Où entrer, où sortir (gain/perte)
        4. **R/R** : Le rapport gain/risque (min 2:1)
        5. **Indicateurs** : Confirment la force du signal
        """)

    with col2:
        st.markdown("""
        **Barème de notation:**

        - 🌟 **80-100** : Signal excellent
        - ✅ **60-79** : Signal bon
        - 👀 **40-59** : À surveiller
        - ⏸️ **0-39** : Attendre

        Plus le score est élevé, plus les conditions sont réunies.
        """)

    # Avertissement
    st.markdown("---")
    st.warning("""
    ⚠️ **Important** : Ces indicateurs sont des **outils d'aide à la décision**, pas des garanties de performance.
    Utilisez-les toujours en complément de votre propre analyse et gestion du risque.

    **Ne jamais**:
    - Investir de l'argent que vous ne pouvez pas perdre
    - Suivre un signal aveuglément sans comprendre
    - Négliger le stop loss
    - Investir sans diversification
    """)

    # Ressources
    st.markdown("---")
    st.subheader("📖 Pour aller plus loin")

    st.markdown("""
    **Ressources recommandées:**

    - 📈 **Backtesting** : Testez les stratégies sur l'historique
    - 🏆 **Top Sélections** : Découvrez les meilleurs classements
    - 🔔 **Alertes** : Soyez notifié des nouveaux signaux
    - 📊 **Dashboard** : Vue d'ensemble de vos actions

    **Documentation:**
    - `NOUVELLES_STRATEGIES.md` : Guide complet des 6 stratégies
    - `NAVIGATION.md` : Comment utiliser l'application
    """)


if __name__ == "__main__":
    render_glossaire()
