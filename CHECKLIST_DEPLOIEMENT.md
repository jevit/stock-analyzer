# ✅ Checklist de Déploiement

Utilisez cette checklist avant de déployer votre application pour vous assurer que tout est prêt.

---

## 📋 Avant le déploiement

### 1. Vérification du code

- [ ] Le code fonctionne localement sans erreur
- [ ] Vous avez testé avec `streamlit run app/main.py`
- [ ] Les dépendances sont à jour dans `requirements.txt`
- [ ] Pas de chemins absolus en dur dans le code (utilisez des chemins relatifs)

### 2. Fichiers de configuration

- [ ] `.gitignore` est présent et configuré
- [ ] `.streamlit/config.toml` existe
- [ ] `runtime.txt` spécifie Python 3.11
- [ ] `requirements.txt` contient toutes les dépendances nécessaires

### 3. Secrets et variables d'environnement

- [ ] Les fichiers `.env` et `secrets.toml` sont dans `.gitignore`
- [ ] Vous avez préparé vos secrets (tokens Telegram, passwords email)
- [ ] `.env.example` et `secrets.toml.example` sont à jour

### 4. Code sécurisé

- [ ] Aucun secret (token, password) n'est écrit en dur dans le code
- [ ] Pas de clés API exposées dans les fichiers versionnés
- [ ] Le fichier `.env` n'est PAS committé

---

## 🔧 Préparation GitHub

### 1. Repository Git

```bash
# Vérifier le statut
git status

# Ajouter tous les fichiers
git add .

# Committer
git commit -m "Prêt pour le déploiement"

# Vérifier qu'aucun secret n'est committé
git log --all --full-history -- .env
git log --all --full-history -- .streamlit/secrets.toml
# Ces commandes ne doivent rien retourner
```

### 2. Créer le repository GitHub

- [ ] Créé un nouveau repo sur [github.com/new](https://github.com/new)
- [ ] Nommé le repo (ex: `stock-analyzer`)
- [ ] Choisi "Public" ou "Private"
- [ ] PAS de README (vous en avez déjà un)

### 3. Pousser le code

```bash
# Ajouter le remote
git remote add origin https://github.com/VOTRE_USERNAME/stock-analyzer.git

# Pousser le code
git branch -M main
git push -u origin main

# Vérifier sur GitHub que tout est bien poussé
```

---

## 🚀 Déploiement Streamlit Cloud

### 1. Connexion

- [ ] Compte créé sur [share.streamlit.io](https://share.streamlit.io)
- [ ] Connecté avec votre compte GitHub
- [ ] Autorisé Streamlit Cloud à accéder à vos repos

### 2. Création de l'app

- [ ] Cliqué sur "New app"
- [ ] Sélectionné le bon repository : `stock-analyzer`
- [ ] Branch : `main`
- [ ] Main file path : `app/main.py` ⚠️ **Important !**
- [ ] Choisi un nom d'URL (ex: `mon-stock-analyzer`)

### 3. Configuration des secrets (optionnel)

Si vous voulez les alertes Telegram/Email :

- [ ] Dans Settings → Secrets
- [ ] Copié le contenu de `.streamlit/secrets.toml.example`
- [ ] Remplacé par vos vraies valeurs
- [ ] Sauvegardé

Exemple de secrets :
```toml
[telegram]
token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
chat_id = "987654321"

[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
from = "mon.email@gmail.com"
password = "xxxx xxxx xxxx xxxx"
to = "mon.email@gmail.com"
```

### 4. Déploiement

- [ ] Cliqué sur "Deploy!"
- [ ] Attendu que le build se termine (2-3 minutes)
- [ ] Vérifié les logs en cas d'erreur
- [ ] Testé l'app sur l'URL fournie

---

## 🧪 Après le déploiement

### 1. Tests fonctionnels

- [ ] L'app se charge sans erreur
- [ ] Vous pouvez charger une watchlist
- [ ] Les graphiques s'affichent correctement
- [ ] Les données sont téléchargées (yfinance fonctionne)
- [ ] L'export CSV fonctionne

### 2. Tests des alertes (si configurées)

- [ ] Testé l'envoi d'une alerte Telegram
- [ ] Testé l'envoi d'un email
- [ ] Les alertes arrivent correctement

### 3. Performance

- [ ] L'app se charge en moins de 10 secondes
- [ ] Le cache fonctionne (les données ne se rechargent pas à chaque fois)
- [ ] Pas d'erreurs dans les logs

---

## 🔄 Mises à jour futures

Chaque fois que vous voulez mettre à jour l'app :

```bash
# 1. Faire vos modifications
# 2. Tester localement
streamlit run app/main.py

# 3. Committer
git add .
git commit -m "Description des changements"

# 4. Pousser
git push

# 5. Streamlit Cloud redéploie automatiquement ! 🎉
```

---

## 🆘 Dépannage rapide

### L'app ne démarre pas

**Vérifier** :
1. Les logs sur Streamlit Cloud
2. Que `app/main.py` est le bon chemin
3. Que `requirements.txt` est complet
4. Qu'il n'y a pas de chemins absolus dans le code

### "ModuleNotFoundError"

**Solution** : Ajouter le module manquant dans `requirements.txt`

```bash
# Localement
pip install <module_manquant>
pip freeze > requirements.txt

# Puis commit et push
git add requirements.txt
git commit -m "Ajout dépendance manquante"
git push
```

### Les secrets ne fonctionnent pas

**Vérifier** :
1. Le format TOML est correct (indentation, guillemets)
2. Les secrets sont dans Settings → Secrets sur Streamlit Cloud
3. Vous utilisez `st.secrets["cle"]` dans le code

### L'app est lente

**C'est normal** pour le free tier (1 GB RAM).

**Optimisations** :
- Réduire le nombre de tickers
- Utiliser le cache (`@st.cache_data`)
- Charger les données par petits lots

---

## 📊 Ressources utiles

- **Guide complet** : [DEPLOIEMENT.md](DEPLOIEMENT.md)
- **Documentation Streamlit Cloud** : [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- **Forum d'aide** : [discuss.streamlit.io](https://discuss.streamlit.io)

---

**Bon déploiement ! 🚀**

Une fois terminé, n'oubliez pas de partager l'URL de votre app !
