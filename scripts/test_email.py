#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Email.

Usage: python scripts/test_email.py
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import os
from dotenv import load_dotenv

# Reload .env
load_dotenv(override=True)

print("=" * 60)
print("TEST CONFIGURATION EMAIL")
print("=" * 60)
print()

# Check .env file
env_file = PROJECT_ROOT / ".env"
if not env_file.exists():
    print("❌ ERREUR: Le fichier .env n'existe pas!")
    print(f"   Créez-le à: {env_file}")
    print()
    print("Copiez .env.example en .env et remplissez vos valeurs:")
    print(f"   copy {PROJECT_ROOT}\\.env.example {PROJECT_ROOT}\\.env")
    sys.exit(1)

print(f"✅ Fichier .env trouvé: {env_file}")
print()

# Check environment variables
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT", "587")
email_from = os.getenv("EMAIL_FROM")
email_password = os.getenv("EMAIL_PASSWORD")
email_to = os.getenv("EMAIL_TO")

print("Configuration actuelle:")
print("-" * 60)

valid_config = True

if smtp_server and smtp_server != "votre_smtp_ici":
    print(f"✅ SMTP_SERVER: {smtp_server}")
else:
    print("❌ SMTP_SERVER: Non configuré")
    valid_config = False

print(f"✅ SMTP_PORT: {smtp_port}")

if email_from and email_from != "votre.email@gmail.com":
    print(f"✅ EMAIL_FROM: {email_from}")
else:
    print("❌ EMAIL_FROM: Non configuré")
    valid_config = False

if email_password and email_password != "votre_mot_de_passe_app":
    masked = "*" * len(email_password)
    print(f"✅ EMAIL_PASSWORD: {masked}")
else:
    print("❌ EMAIL_PASSWORD: Non configuré")
    valid_config = False

if email_to and email_to != "votre.email@gmail.com":
    print(f"✅ EMAIL_TO: {email_to}")
else:
    print("❌ EMAIL_TO: Non configuré")
    valid_config = False

print("-" * 60)
print()

if not valid_config:
    print("⚠️  Configuration incomplète!")
    print()
    print("CONFIGURATION EMAIL POUR GMAIL:")
    print()
    print("1️⃣  Activez la validation en 2 étapes:")
    print("   • Allez sur: https://myaccount.google.com/security")
    print("   • Activez 'Validation en 2 étapes'")
    print()
    print("2️⃣  Créez un mot de passe d'application:")
    print("   • Allez sur: https://myaccount.google.com/apppasswords")
    print("   • Sélectionnez 'Autre' comme nom")
    print("   • Donnez un nom: 'Stock Analyzer'")
    print("   • Copiez le mot de passe de 16 caractères")
    print()
    print(f"3️⃣  Modifiez le fichier .env:")
    print(f"   {env_file}")
    print()
    print("   Exemple pour Gmail:")
    print("   SMTP_SERVER=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_FROM=votre.email@gmail.com")
    print("   EMAIL_PASSWORD=abcd efgh ijkl mnop")
    print("   EMAIL_TO=votre.email@gmail.com")
    print()
    print("   Pour Outlook/Hotmail:")
    print("   SMTP_SERVER=smtp-mail.outlook.com")
    print("   SMTP_PORT=587")
    print()
    print("   Pour Yahoo:")
    print("   SMTP_SERVER=smtp.mail.yahoo.com")
    print("   SMTP_PORT=587")
    print()
    print("4️⃣  Relancez ce script pour tester")
    print()
    sys.exit(1)

# Test connection
print("Test de connexion Email...")
print()

try:
    from src.alerts.email_notifier import EmailNotifier

    notifier = EmailNotifier()

    if not notifier.is_configured():
        print("❌ Configuration invalide détectée par le notifier")
        sys.exit(1)

    print(f"📤 Envoi d'un email de test à {email_to}...")
    print()

    success = notifier.test_connection()

    if success:
        print()
        print("=" * 60)
        print("✅ SUCCÈS!")
        print("=" * 60)
        print()
        print(f"L'email de test a été envoyé à: {email_to}")
        print("Vérifiez votre boîte de réception (et les spams).")
        print()
        print("Vous pouvez maintenant:")
        print("  • Utiliser la page Alertes dans l'application")
        print("  • Configurer le scanner automatique")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ ÉCHEC DE L'ENVOI")
        print("=" * 60)
        print()
        print("Vérifications:")
        print("  1. Le serveur SMTP est-il correct?")
        print(f"     Actuellement: {smtp_server}:{smtp_port}")
        print()
        print("  2. L'adresse email est-elle correcte?")
        print(f"     De: {email_from}")
        print(f"     À:  {email_to}")
        print()
        print("  3. Le mot de passe d'application est-il correct?")
        print("     Utilisez un mot de passe d'app, pas votre mot de passe Gmail")
        print("     Créez-en un sur: https://myaccount.google.com/apppasswords")
        print()
        print("  4. Avez-vous une connexion internet?")
        print()
        print("  5. Pour Gmail, avez-vous activé la validation en 2 étapes?")
        print()

except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERREUR")
    print("=" * 60)
    print()
    print(f"Erreur lors du test: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
