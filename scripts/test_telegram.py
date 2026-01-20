#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Telegram.

Usage: python scripts/test_telegram.py
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
print("TEST CONFIGURATION TELEGRAM")
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
token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("Configuration actuelle:")
print("-" * 60)

if token:
    if token == "your_bot_token_here" or token == "votre_token_ici":
        print("❌ TELEGRAM_TOKEN: Non configuré (valeur par défaut)")
        token = None
    else:
        # Mask token for security
        masked = token[:10] + "..." + token[-5:] if len(token) > 15 else "***"
        print(f"✅ TELEGRAM_TOKEN: {masked}")
else:
    print("❌ TELEGRAM_TOKEN: Non défini")

if chat_id:
    if chat_id == "your_chat_id_here" or chat_id == "votre_chat_id_ici":
        print("❌ TELEGRAM_CHAT_ID: Non configuré (valeur par défaut)")
        chat_id = None
    else:
        print(f"✅ TELEGRAM_CHAT_ID: {chat_id}")
else:
    print("❌ TELEGRAM_CHAT_ID: Non défini")

print("-" * 60)
print()

if not token or not chat_id:
    print("⚠️  Configuration incomplète!")
    print()
    print("ÉTAPES POUR CONFIGURER TELEGRAM:")
    print()
    print("1️⃣  Créer un bot Telegram:")
    print("   • Ouvrez Telegram et cherchez: @BotFather")
    print("   • Envoyez: /newbot")
    print("   • Donnez un nom à votre bot (ex: Mon Stock Analyzer)")
    print("   • Donnez un username (ex: mon_stock_bot)")
    print("   • Copiez le TOKEN fourni (ressemble à: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print()
    print("2️⃣  Obtenir votre Chat ID:")
    print("   • Cherchez sur Telegram: @userinfobot")
    print("   • Envoyez: /start")
    print("   • Copiez votre ID (un nombre comme: 123456789)")
    print()
    print("3️⃣  Démarrez une conversation avec votre bot:")
    print("   • Cherchez votre bot par son username")
    print("   • Cliquez sur START ou envoyez /start")
    print("   • (Important: le bot ne peut envoyer que si vous avez démarré!)")
    print()
    print(f"4️⃣  Modifiez le fichier .env:")
    print(f"   {env_file}")
    print()
    print("   Remplacez:")
    print("   TELEGRAM_TOKEN=votre_token_ici")
    print("   TELEGRAM_CHAT_ID=votre_chat_id_ici")
    print()
    print("   Par vos vraies valeurs (sans guillemets):")
    print("   TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("   TELEGRAM_CHAT_ID=123456789")
    print()
    print("5️⃣  Relancez ce script pour tester")
    print()
    sys.exit(1)

# Test connection
print("Test de connexion Telegram...")
print()

try:
    from src.alerts.telegram import TelegramNotifier

    notifier = TelegramNotifier()

    if not notifier.is_configured():
        print("❌ Configuration invalide détectée par le notifier")
        sys.exit(1)

    print("📤 Envoi d'un message de test...")

    test_message = """
🔔 <b>Test de connexion réussi!</b>

Votre bot Telegram est correctement configuré pour Stock Analyzer.

Vous recevrez maintenant des alertes quand des signaux forts seront détectés.

✅ Configuration validée
    """.strip()

    success = notifier.send_message(test_message)

    if success:
        print()
        print("=" * 60)
        print("✅ SUCCÈS!")
        print("=" * 60)
        print()
        print("Le message de test a été envoyé.")
        print("Vérifiez votre Telegram pour le voir.")
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
        print("  1. Avez-vous démarré une conversation avec votre bot?")
        print("     Cherchez votre bot sur Telegram et envoyez /start")
        print()
        print("  2. Le token est-il correct?")
        print("     Vérifiez dans .env (pas d'espaces, pas de guillemets)")
        print()
        print("  3. Le Chat ID est-il correct?")
        print("     C'est un nombre, pas un username")
        print()
        print("  4. Avez-vous une connexion internet?")
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
