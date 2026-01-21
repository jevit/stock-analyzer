# 🚀 Guide de Déploiement - Stock Analyzer

Ce guide vous explique comment déployer gratuitement votre application Stock Analyzer sur Internet.

---

## 📋 Table des matières

1. [Streamlit Community Cloud (Recommandé)](#streamlit-community-cloud-recommandé)
2. [Hugging Face Spaces](#hugging-face-spaces)
3. [Render](#render)
4. [Configuration des Secrets](#configuration-des-secrets)
5. [Dépannage](#dépannage)

---

## 🥇 Streamlit Community Cloud (Recommandé)

**La solution la plus simple pour déployer une app Streamlit !**

### Avantages
- ✅ **100% gratuit** pour les apps publiques
- ✅ Déploiement en **1 clic** depuis GitHub
- ✅ Builds automatiques à chaque push
- ✅ Gestion facile des secrets (tokens, API keys)
- ✅ URL personnalisée : `votreapp.streamlit.app`

### Limitations
- 1 GB RAM
- 1 CPU partagé
- L'app s'endort après ~7 jours d'inactivité (redémarre au premier accès)
- ⚠️ **Nécessite un repository GitHub PUBLIC**

> 🔒 **Votre repo est privé ?** Consultez [DEPLOIEMENT_REPO_PRIVE.md](DEPLOIEMENT_REPO_PRIVE.md) pour vos options.

### Étapes de déploiement

#### 1. Préparer votre code sur GitHub

```bash
# Si ce n'est pas déjà fait, initialisez git
git init
git add .
git commit -m "Initial commit - Stock Analyzer"

# Créez un repo sur GitHub et poussez votre code
git remote add origin https://github.com/VOTRE_USERNAME/stock-analyzer.git
git branch -M main
git push -u origin main
```

#### 2. Déployer sur Streamlit Cloud

1. **Allez sur [share.streamlit.io](https://share.streamlit.io)**

2. **Connectez-vous** avec votre compte GitHub

3. **Cliquez sur "New app"**

4. **Remplissez le formulaire** :
   - **Repository** : Sélectionnez votre repo `stock-analyzer`
   - **Branch** : `main`
   - **Main file path** : `app/main.py`
   - **App URL** : Choisissez un nom (ex: `mon-stock-analyzer`)

5. **Cliquez sur "Deploy"**

🎉 **C'est tout !** Votre app sera disponible à l'adresse :
`https://mon-stock-analyzer.streamlit.app`

#### 3. Configurer les secrets (optionnel)

Si vous voulez activer les alertes Telegram/Email :

1. Dans votre app sur Streamlit Cloud, cliquez sur **"Settings"** (⚙️)
2. Allez dans **"Secrets"**
3. Copiez le contenu de `.streamlit/secrets.toml.example`
4. Remplacez les valeurs par vos vraies credentials
5. Cliquez sur **"Save"**

Exemple :
```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
from = "mon.email@gmail.com"
password = "xxxx xxxx xxxx xxxx"
to = "mon.email@gmail.com"

[telegram]
token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
chat_id = "987654321"
```

#### 4. Mises à jour automatiques

Chaque fois que vous poussez du code sur GitHub :
```bash
git add .
git commit -m "Amélioration des graphiques"
git push
```

→ Streamlit Cloud **redéploie automatiquement** votre app ! 🔄

---

## 🥈 Hugging Face Spaces

**Alternative populaire dans la communauté Data Science**

### Avantages
- ✅ Gratuit (2 CPU, 16 GB stockage)
- ✅ Support natif de Streamlit
- ✅ Communauté ML/Data Science active
- ✅ Peut rester actif plus longtemps

### Étapes de déploiement

#### 1. Créer un Space

1. **Allez sur [huggingface.co/spaces](https://huggingface.co/new-space)**
2. **Créez un compte** (gratuit)
3. **Cliquez sur "Create new Space"**
4. **Remplissez** :
   - **Space name** : `stock-analyzer`
   - **License** : MIT
   - **Select the Space SDK** : **Streamlit**
   - **Space hardware** : CPU basic (gratuit)

#### 2. Uploader vos fichiers

**Option A : Via l'interface web**
- Cliquez sur "Files" puis "Add file"
- Uploadez tous vos fichiers

**Option B : Via Git (recommandé)**
```bash
git clone https://huggingface.co/spaces/VOTRE_USERNAME/stock-analyzer
cd stock-analyzer

# Copiez tous vos fichiers ici
cp -r /chemin/vers/votre/stock-analyzer/* .

git add .
git commit -m "Initial deploy"
git push
```

#### 3. Créer app.py à la racine

Hugging Face nécessite un fichier `app.py` à la racine :

```python
# app.py
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main app
from app.main import main

if __name__ == "__main__":
    main()
```

#### 4. Configurer les secrets

1. Allez dans **"Settings"** de votre Space
2. Cliquez sur **"Repository secrets"**
3. Ajoutez vos variables (format clé=valeur) :
   - `TELEGRAM_TOKEN=votre_token`
   - `TELEGRAM_CHAT_ID=votre_chat_id`
   - etc.

---

## 🥉 Render

**Service cloud polyvalent avec free tier généreux**

### Avantages
- ✅ 750 heures gratuites/mois
- ✅ Déploiement depuis GitHub
- ✅ Plus de contrôle sur l'environnement

### Inconvénients
- ⚠️ S'endort après 15 min d'inactivité
- ⚠️ Redémarrage lent (~30-60 secondes)

### Étapes de déploiement

#### 1. Créer un compte

1. **Allez sur [render.com](https://render.com)**
2. **Sign up** (gratuit)
3. **Connectez votre compte GitHub**

#### 2. Créer un Web Service

1. **Cliquez sur "New +"** → **"Web Service"**
2. **Sélectionnez votre repo** `stock-analyzer`
3. **Remplissez** :
   - **Name** : `stock-analyzer`
   - **Region** : Frankfurt (le plus proche de l'Europe)
   - **Branch** : `main`
   - **Runtime** : Python 3
   - **Build Command** :
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command** :
     ```bash
     streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0
     ```
   - **Instance Type** : **Free**

4. **Cliquez sur "Create Web Service"**

#### 3. Configurer les variables d'environnement

1. Dans votre service, allez dans **"Environment"**
2. Ajoutez vos secrets :
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - etc.

#### 4. Accéder à votre app

Votre app sera disponible à : `https://stock-analyzer-xxxx.onrender.com`

**Note** : Le premier chargement peut prendre 30-60 secondes si l'app s'est endormie.

---

## 🔐 Configuration des Secrets

### Pour Telegram

1. **Créer un bot** :
   - Cherchez `@BotFather` sur Telegram
   - Envoyez `/newbot`
   - Suivez les instructions
   - **Copiez le token**

2. **Obtenir votre Chat ID** :
   - Cherchez `@userinfobot` sur Telegram
   - Envoyez `/start`
   - **Copiez votre ID**

3. **Démarrer une conversation** :
   - Cherchez votre bot par son nom
   - Envoyez `/start`
   - ⚠️ Important pour que le bot puisse vous envoyer des messages

### Pour Email (Gmail)

1. **Activer la validation en 2 étapes** :
   - Allez sur [myaccount.google.com](https://myaccount.google.com)
   - Sécurité → Validation en 2 étapes

2. **Créer un mot de passe d'application** :
   - [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Sélectionnez "Mail" et votre appareil
   - **Copiez le mot de passe** (16 caractères)

3. **Utilisez ce mot de passe** dans vos secrets (pas votre mot de passe Gmail normal)

---

## 🔧 Dépannage

### L'app ne démarre pas

**Vérifiez les logs** :
- Streamlit Cloud : Onglet "Logs"
- Hugging Face : Onglet "Logs"
- Render : Section "Logs"

**Erreurs courantes** :
- ❌ `ModuleNotFoundError` → Vérifiez `requirements.txt`
- ❌ `FileNotFoundError` → Vérifiez les chemins (utilisez des chemins relatifs)
- ❌ Port binding error → Sur Render, utilisez `$PORT`

### L'app est lente

**C'est normal pour le free tier !**
- Streamlit Cloud : 1 GB RAM limitée
- Render : S'endort après 15 min

**Solutions** :
- Optimisez le cache avec `@st.cache_data`
- Réduisez le nombre de tickers analysés
- Utilisez des watchlists plus petites

### Les secrets ne fonctionnent pas

**Vérifiez le format** :
- Streamlit Cloud : Format TOML
- Hugging Face : Variables d'environnement (clé=valeur)
- Render : Variables d'environnement

**Testez** :
```python
import streamlit as st
st.write(st.secrets)  # Affiche les secrets (temporairement)
```

### Le cache ne persiste pas

**C'est normal !** Les plateformes gratuites ne persistent pas les fichiers.

**Solutions** :
- Le cache sera recréé à chaque session
- Les données sont téléchargées à la demande
- C'est l'inconvénient du free tier

---

## 📊 Comparaison des plateformes

| Critère | Streamlit Cloud | Hugging Face | Render |
|---------|----------------|--------------|--------|
| **Prix** | Gratuit | Gratuit | Gratuit (750h) |
| **RAM** | 1 GB | 2 GB | 512 MB |
| **Facilité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Vitesse** | Rapide | Rapide | Lent (cold start) |
| **Sleep** | Après 7j | Rare | Après 15 min |
| **Build auto** | ✅ | ✅ | ✅ |
| **Custom URL** | ✅ | ✅ | ✅ |
| **Best for** | Apps Streamlit | ML/Data Science | Apps génériques |

---

## ✅ Recommandation finale

Pour votre **Stock Analyzer**, nous recommandons :

🥇 **Streamlit Community Cloud** - Simple, rapide, conçu pour Streamlit

Déployez en 5 minutes : [share.streamlit.io](https://share.streamlit.io) 🚀

---

## 🆘 Besoin d'aide ?

- **Documentation Streamlit Cloud** : [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- **Forum Streamlit** : [discuss.streamlit.io](https://discuss.streamlit.io)
- **Discord Hugging Face** : [hf.co/join/discord](https://hf.co/join/discord)

---

*Bon déploiement ! 🚀*
