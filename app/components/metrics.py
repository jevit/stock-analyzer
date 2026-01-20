"""
Composants de métriques avec tooltips explicatifs.
"""
import streamlit as st
from app.utils.tooltips import TOOLTIPS


def metric_with_tooltip(label: str, value: str, tooltip_key: str = None, delta: str = None, delta_color: str = "off", help_text: str = None):
    """
    Affiche une métrique avec tooltip explicatif.

    Args:
        label: Label de la métrique
        value: Valeur à afficher
        tooltip_key: Clé du tooltip dans TOOLTIPS (optionnel)
        delta: Variation (optionnel)
        delta_color: Couleur du delta
        help_text: Texte d'aide personnalisé (prioritaire sur tooltip_key)
    """
    # Détermine le texte d'aide
    help_msg = help_text if help_text else (TOOLTIPS.get(tooltip_key, "") if tooltip_key else "")

    # Si on a un tooltip, on l'affiche via un expander discret ou markdown
    if help_msg:
        # Créer le label avec une icône d'info
        display_label = f"{label} ℹ️"
    else:
        display_label = label

    # Afficher la métrique
    st.metric(
        display_label,
        value,
        delta=delta,
        delta_color=delta_color
    )

    # Afficher le tooltip en petit sous la métrique si présent
    if help_msg:
        with st.expander("💡 Explication", expanded=False):
            st.markdown(help_msg)


def show_tooltip_info(key: str):
    """
    Affiche juste l'icône info avec tooltip au survol.

    Args:
        key: Clé du tooltip dans TOOLTIPS
    """
    help_msg = TOOLTIPS.get(key, "")
    if help_msg:
        st.markdown(f"ℹ️", help=help_msg)


def render_indicator_card(title: str, value: str, description: str, tooltip_key: str = None, status: str = None):
    """
    Render une carte d'indicateur avec description et tooltip.

    Args:
        title: Titre de l'indicateur
        value: Valeur actuelle
        description: Description courte
        tooltip_key: Clé pour tooltip détaillé
        status: Statut (ex: "Bon", "Attention", etc.)
    """
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{title}**")
            st.markdown(f"### {value}")
            st.caption(description)
            if status:
                if "Bon" in status or "Fort" in status or "Excellent" in status:
                    st.success(f"✅ {status}")
                elif "Attention" in status or "Risque" in status or "Élevé" in status:
                    st.warning(f"⚠️ {status}")
                else:
                    st.info(f"ℹ️ {status}")

        with col2:
            if tooltip_key and tooltip_key in TOOLTIPS:
                with st.expander("?"):
                    st.markdown(TOOLTIPS[tooltip_key])
