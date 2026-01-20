"""
Alerts configuration page.
"""
import streamlit as st
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from config.settings import get_settings
from src.alerts.telegram import TelegramNotifier
from src.alerts.email_notifier import EmailNotifier
from src.alerts.history import AlertHistory


def render_alerts_page():
    """Render the alerts configuration page."""
    st.title("🔔 Configuration des Alertes")

    st.markdown("""
    Configurez les alertes automatiques pour être notifié quand un signal fort est détecté.
    """)

    # Email Configuration Section (PRIORITÉ)
    st.markdown("---")
    st.header("📧 Configuration Email (Recommandé)")

    settings = get_settings()
    email_notifier = EmailNotifier()

    # Status indicator
    if email_notifier.is_configured():
        st.success("✅ Email est configuré")
    else:
        st.warning("⚠️ Email n'est pas configuré")

    with st.expander("📖 Comment configurer l'email?", expanded=not email_notifier.is_configured()):
        st.markdown("""
        ### Configuration Gmail (le plus simple)

        **1. Activez la validation en 2 étapes:**
        - Allez sur [https://myaccount.google.com/security](https://myaccount.google.com/security)
        - Activez **Validation en 2 étapes** (si pas déjà fait)

        **2. Créez un mot de passe d'application:**
        - Allez sur [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
        - Sélectionnez "Autre" comme nom
        - Donnez un nom: "Stock Analyzer"
        - Cliquez sur **Générer**
        - **Copiez** le mot de passe de 16 caractères (ex: abcd efgh ijkl mnop)

        **3. Configurez le fichier .env:**

        Créez/modifiez le fichier `.env` à la racine du projet:
        ```
        SMTP_SERVER=smtp.gmail.com
        SMTP_PORT=587
        EMAIL_FROM=votre.email@gmail.com
        EMAIL_PASSWORD=abcd efgh ijkl mnop
        EMAIL_TO=votre.email@gmail.com
        ```

        **4. Redémarrez l'application**

        ---

        ### Autres fournisseurs d'email

        **Outlook/Hotmail:**
        ```
        SMTP_SERVER=smtp-mail.outlook.com
        SMTP_PORT=587
        ```

        **Yahoo:**
        ```
        SMTP_SERVER=smtp.mail.yahoo.com
        SMTP_PORT=587
        ```

        **ProtonMail:**
        ```
        SMTP_SERVER=smtp.protonmail.ch
        SMTP_PORT=587
        ```
        """)

    # Test email connection
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧪 Tester Email", disabled=not email_notifier.is_configured(), key="test_email"):
            with st.spinner("Envoi du message test..."):
                if email_notifier.test_connection():
                    st.success("✅ Email de test envoyé! Vérifiez votre boîte de réception.")
                else:
                    st.error("❌ Échec de l'envoi. Vérifiez vos paramètres.")

    with col2:
        # Manual email alert trigger
        if st.button("📤 Envoyer alerte Email", disabled=not email_notifier.is_configured(), key="send_email"):
            if "analyses" in st.session_state and st.session_state["analyses"]:
                analyses = st.session_state["analyses"]
                min_score = st.session_state.get("alert_min_score", 75)

                subject, html, text = email_notifier.format_alert_email(analyses, min_score=min_score)

                if subject:
                    with st.spinner("Envoi de l'alerte..."):
                        if email_notifier.send_email(subject, html, text):
                            st.success("✅ Alerte envoyée par email!")
                        else:
                            st.error("❌ Échec de l'envoi")
                else:
                    st.info(f"Aucun signal avec score >= {min_score}")
            else:
                st.warning("Chargez d'abord des données depuis le tableau de bord")

    # Telegram Configuration Section (Alternative)
    st.markdown("---")
    st.header("📱 Configuration Telegram (Alternatif)")

    notifier = TelegramNotifier()

    # Status indicator
    if notifier.is_configured():
        st.success("✅ Telegram est configuré")
    else:
        st.warning("⚠️ Telegram n'est pas configuré")

    with st.expander("📖 Comment configurer Telegram?", expanded=not notifier.is_configured()):
        st.markdown("""
        ### Étapes de configuration

        **1. Créer un bot Telegram:**
        1. Ouvrez Telegram et cherchez `@BotFather`
        2. Envoyez `/newbot`
        3. Donnez un nom à votre bot (ex: "Mon Stock Analyzer")
        4. Copiez le **token** fourni

        **2. Obtenir votre Chat ID:**
        1. Cherchez `@userinfobot` sur Telegram
        2. Envoyez `/start`
        3. Copiez votre **ID** (nombre)

        **3. Configurer l'application:**

        Créez un fichier `.env` à la racine du projet avec:
        ```
        TELEGRAM_TOKEN=votre_token_ici
        TELEGRAM_CHAT_ID=votre_chat_id_ici
        ```

        **4. Redémarrez l'application**
        """)

    # Test connection button
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧪 Tester la connexion", disabled=not notifier.is_configured()):
            with st.spinner("Envoi du message test..."):
                if notifier.test_connection():
                    st.success("✅ Message test envoyé! Vérifiez Telegram.")
                else:
                    st.error("❌ Échec de l'envoi. Vérifiez vos paramètres.")

    with col2:
        # Manual alert trigger
        if st.button("📤 Envoyer alerte maintenant", disabled=not notifier.is_configured()):
            if "analyses" in st.session_state and st.session_state["analyses"]:
                analyses = st.session_state["analyses"]
                min_score = st.session_state.get("alert_min_score", 75)

                message = notifier.format_alert_message(analyses, min_score=min_score)

                if message:
                    with st.spinner("Envoi de l'alerte..."):
                        if notifier.send_message(message):
                            st.success("✅ Alerte envoyée!")
                        else:
                            st.error("❌ Échec de l'envoi")
                else:
                    st.info(f"Aucun signal avec score >= {min_score}")
            else:
                st.warning("Chargez d'abord des données depuis le tableau de bord")

    # Alert Settings
    st.markdown("---")
    st.header("⚙️ Paramètres des Alertes")

    col1, col2 = st.columns(2)

    with col1:
        min_score = st.slider(
            "Score minimum pour alerter",
            min_value=50,
            max_value=95,
            value=st.session_state.get("alert_min_score", 75),
            step=5,
            help="🎯 Score minimum pour déclencher une alerte. Seuls les signaux avec un score >= à cette valeur vous seront notifiés. 75+ = signaux forts, 85+ = signaux excellents."
        )
        st.session_state["alert_min_score"] = min_score

    with col2:
        cooldown = st.slider(
            "Délai entre alertes (heures)",
            min_value=1,
            max_value=72,
            value=st.session_state.get("alert_cooldown", 24),
            help="⏱️ Période de refroidissement pour éviter les alertes répétées. Temps minimum avant de recevoir une nouvelle alerte pour le même ticker et la même stratégie. 24h recommandé."
        )
        st.session_state["alert_cooldown"] = cooldown

    # Alert History
    st.markdown("---")
    st.header("📜 Historique des Alertes")

    history = AlertHistory()
    recent_alerts = history.get_recent_alerts(hours=72)

    if recent_alerts:
        st.markdown(f"**{len(recent_alerts)} alertes envoyées ces dernières 72h:**")

        # Create a simple table
        for alert in recent_alerts[:20]:
            timestamp = datetime.fromisoformat(alert.timestamp)
            time_str = timestamp.strftime("%d/%m %H:%M")

            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.text(time_str)
            with col2:
                st.text(f"📌 {alert.ticker}")
            with col3:
                st.text(f"📊 {alert.strategy}")
            with col4:
                st.text(f"🎯 {alert.score}")

        if len(recent_alerts) > 20:
            st.caption(f"... et {len(recent_alerts) - 20} autres")

        # Clear history button
        if st.button("🗑️ Effacer l'historique"):
            history.clear_history()
            st.success("Historique effacé")
            st.rerun()
    else:
        st.info("Aucune alerte envoyée récemment")

    # Auto Scanner Section
    st.markdown("---")
    st.header("🤖 Scanner Automatique")

    st.markdown("""
    Le scanner automatique peut être exécuté périodiquement pour détecter les nouveaux signaux
    et envoyer des alertes Telegram.
    """)

    with st.expander("📖 Comment planifier le scan automatique?"):
        st.markdown("""
        ### Windows - Planificateur de tâches

        1. Ouvrez le **Planificateur de tâches** Windows
        2. Cliquez sur **Créer une tâche de base**
        3. Donnez un nom: "Stock Analyzer Scanner"
        4. **Déclencheur**: Quotidien à 18h00 (après la fermeture des marchés)
        5. **Action**: Démarrer un programme
           - Programme: `python`
           - Arguments: `scripts\\auto_scanner.py --min-score 75`
           - Démarrer dans: `C:\\chemin\\vers\\stock-analyzer`

        ### Linux/Mac - Cron

        Éditez votre crontab avec `crontab -e` et ajoutez:
        ```
        # Scan quotidien à 18h (jours de semaine)
        0 18 * * 1-5 cd /chemin/vers/stock-analyzer && python scripts/auto_scanner.py
        ```

        ### Options du scanner

        ```
        python scripts/auto_scanner.py --help

        Options:
          --min-score     Score minimum (défaut: 75)
          --cooldown      Heures entre alertes identiques (défaut: 24)
          --dry-run       Tester sans envoyer d'alertes
          --force-refresh Forcer le rafraîchissement des données
          --verbose       Logs détaillés
        ```
        """)

    # Manual scan trigger
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Lancer un scan maintenant"):
            with st.spinner("Scan en cours..."):
                try:
                    # Import and run scanner
                    project_root = Path(__file__).parent.parent.parent
                    sys.path.insert(0, str(project_root))

                    from scripts.auto_scanner import run_scan

                    results = run_scan(
                        min_score=min_score,
                        dry_run=False,
                        cooldown_hours=cooldown
                    )

                    # Display results
                    st.success("Scan terminé!")

                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Tickers scannés", results["tickers_scanned"])
                    col_b.metric("Signaux détectés", results["signals_found"])
                    col_c.metric("Alertes envoyées", results["alerts_sent"])

                    if results["alerts_skipped_duplicate"] > 0:
                        st.info(f"ℹ️ {results['alerts_skipped_duplicate']} alertes ignorées (doublons)")

                    if results["errors"]:
                        for err in results["errors"]:
                            st.warning(f"⚠️ {err}")

                except Exception as e:
                    st.error(f"Erreur: {e}")

    with col2:
        if st.button("🧪 Test (sans envoyer)"):
            with st.spinner("Scan de test en cours..."):
                try:
                    project_root = Path(__file__).parent.parent.parent
                    sys.path.insert(0, str(project_root))

                    from scripts.auto_scanner import run_scan

                    results = run_scan(
                        min_score=min_score,
                        dry_run=True,
                        cooldown_hours=cooldown
                    )

                    st.success("Scan de test terminé!")

                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Tickers scannés", results["tickers_scanned"])
                    col_b.metric("Signaux trouvés", results["signals_found"])
                    col_c.metric("Alertes à envoyer", results["signals_found"] - results["alerts_skipped_duplicate"])

                except Exception as e:
                    st.error(f"Erreur: {e}")
