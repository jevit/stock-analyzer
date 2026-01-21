# 🔒 Déploiement avec un Repository Privé

Votre repository est privé ? Voici vos options pour déployer gratuitement.

---

## ⚠️ Problème

**Streamlit Community Cloud gratuit** nécessite un repository **PUBLIC** sur GitHub.

Si votre repo est privé, vous avez plusieurs options :

---

## 🎯 Solutions

### Option 1 : Rendre le repo public (Recommandé) ✅

**La solution la plus simple et gratuite**

#### Avantages
- ✅ Totalement gratuit
- ✅ Fonctionne avec Streamlit Cloud
- ✅ Déploiement automatique
- ✅ Pas de limite

#### Comment faire

1. **Sur GitHub**, allez dans votre repo
2. **Settings** (⚙️) → **General** (tout en bas)
3. Section **Danger Zone** → **Change visibility**
4. Cliquez sur **"Make public"**
5. Confirmez

#### Sécurité

**Ne vous inquiétez pas !** Votre code peut être public en toute sécurité :

✅ **Vos secrets SONT protégés** (tant qu'ils sont dans `.gitignore`) :
- `.env` n'est PAS dans le repo (vérifiez avec `git log --all -- .env`)
- `secrets.toml` n'est PAS dans le repo
- Tokens Telegram/Email sont configurés dans Streamlit Cloud (interface web)

✅ **Partager votre code est sûr** :
- Pas de données sensibles
- Pas de credentials
- C'est juste du code d'analyse technique

❌ **NE rendez PAS public si** :
- Vous avez accidentellement commité des secrets (voir "Nettoyer l'historique" ci-dessous)
- Vous avez des stratégies propriétaires ultra-secrètes

---

### Option 2 : Hugging Face Spaces (Repo Privé OK) ✅

**Fonctionne avec des repos privés !**

#### Avantages
- ✅ Accepte les repos privés
- ✅ Gratuit (2 CPU, 16 GB stockage)
- ✅ Communauté Data Science

#### Comment faire

**Ne pas connecter GitHub** - Upload direct :

1. **Créez un Space** sur [huggingface.co/new-space](https://huggingface.co/new-space)
2. **Nom** : `stock-analyzer`
3. **SDK** : Streamlit
4. **Visibility** : Private (ou Public)
5. **Cliquez sur "Create Space"**

**Upload vos fichiers** :

**Option A : Via l'interface web**
1. Cliquez sur **"Files"** → **"Add file"** → **"Upload files"**
2. Uploadez tous vos fichiers (glissez-déposez tout le dossier)
3. Commit

**Option B : Via Git**
```bash
# Clone le space (pas votre repo GitHub)
git clone https://huggingface.co/spaces/VOTRE_USERNAME/stock-analyzer
cd stock-analyzer

# Copiez vos fichiers
cp -r /chemin/vers/votre/stock-analyzer/* .

# Créez app.py à la racine
cat > app.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from app.main import main

if __name__ == "__main__":
    main()
EOF

# Push
git add .
git commit -m "Deploy app"
git push
```

**Configurer les secrets** :
1. **Settings** de votre Space
2. **Repository secrets**
3. Ajoutez :
   - `TELEGRAM_TOKEN=votre_token`
   - `TELEGRAM_CHAT_ID=votre_chat_id`

✅ **Votre app est en ligne !** → `https://huggingface.co/spaces/VOTRE_USERNAME/stock-analyzer`

---

### Option 3 : Streamlit Cloud avec repo privé (Payant) 💰

Si vous voulez absolument garder le repo privé sur GitHub :

#### Streamlit for Teams
- 💰 **15$/mois** par developer
- ✅ Supporte les repos privés
- ✅ Plus de ressources
- [Site officiel](https://streamlit.io/cloud)

**Pas recommandé** si vous cherchez du gratuit.

---

### Option 4 : Render (Repo Privé via upload manuel)

**Déploiement sans GitHub**

1. **Créez un compte** sur [render.com](https://render.com)
2. **New** → **Web Service** → **"Deploy from Docker image" OU "Public Git repository"**
3. Vous pouvez aussi **uploader un ZIP** de votre code

Mais Render **s'endort après 15 min** d'inactivité sur le free tier.

❌ **Pas idéal** pour une app qu'on veut toujours accessible.

---

## 🧹 Nettoyer l'historique Git (si vous avez commité des secrets)

**IMPORTANT** : Si vous avez accidentellement commité `.env` ou `secrets.toml`, vous **DEVEZ** nettoyer l'historique avant de rendre le repo public.

### Vérifier l'historique

```bash
# Vérifier si .env a été commité
git log --all --full-history -- .env

# Vérifier si secrets.toml a été commité
git log --all --full-history -- .streamlit/secrets.toml
```

Si ces commandes **retournent quelque chose**, vous avez un problème ! 🚨

### Supprimer un fichier de l'historique

```bash
# Installer BFG Repo-Cleaner
# Download depuis: https://rtyley.github.io/bfg-repo-cleaner/

# Supprimer .env de tout l'historique
bfg --delete-files .env

# Nettoyer
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (ATTENTION : écrase l'historique distant)
git push --force
```

**⚠️ ATTENTION** : `git push --force` réécrit l'historique. Faites une backup avant !

### Alternative : Nouveau repo

Si c'est trop compliqué :

```bash
# 1. Sauvegardez votre code actuel
cp -r stock-analyzer stock-analyzer-backup

# 2. Supprimez .git
cd stock-analyzer
rm -rf .git

# 3. Vérifiez que .env n'est PAS là
ls -la .env  # Devrait donner "No such file"

# 4. Nouveau repo Git
git init
git add .
git commit -m "Initial commit - Clean version"

# 5. Créez un NOUVEAU repo sur GitHub
# 6. Push
git remote add origin https://github.com/VOUS/stock-analyzer-new.git
git branch -M main
git push -u origin main
```

---

## 📊 Comparaison des options

| Solution | Gratuit | Repo Privé OK | Facilité | Recommandé |
|----------|---------|---------------|----------|------------|
| **Streamlit + Repo Public** | ✅ | ❌ | ⭐⭐⭐⭐⭐ | 🥇 **OUI** |
| **Hugging Face Spaces** | ✅ | ✅ | ⭐⭐⭐⭐ | 🥈 **OUI** |
| **Streamlit Teams** | ❌ ($15/mois) | ✅ | ⭐⭐⭐⭐⭐ | ❌ Non |
| **Render** | ✅ | ⚠️ (upload) | ⭐⭐⭐ | ⚠️ Moyen |

---

## ✅ Recommandation

### Si vous n'avez PAS de secrets dans l'historique Git :
👉 **Rendre le repo public** + Streamlit Cloud
- Le plus simple et gratuit
- Vos secrets restent privés (dans Streamlit Cloud settings)
- Votre code peut être public sans risque

### Si vous avez des secrets dans l'historique Git :
👉 **Hugging Face Spaces** avec upload manuel
- Pas besoin de GitHub
- Totalement gratuit
- Repo privé OK

---

## 🔐 Checklist de sécurité avant de rendre public

Avant de rendre votre repo public, vérifiez :

```bash
# 1. .env n'est PAS commité
git log --all --full-history -- .env
# Doit retourner : rien

# 2. secrets.toml n'est PAS commité
git log --all --full-history -- .streamlit/secrets.toml
# Doit retourner : rien

# 3. Pas de mots de passe en dur
grep -r "password.*=" --include="*.py" .
# Vérifiez qu'il n'y a que des exemples/configs

# 4. Pas de tokens Telegram
grep -r "[0-9]\{9\}:" --include="*.py" .
# Ne devrait rien trouver dans le code

# 5. Lancez le script de vérification
python scripts/check_deploy.py
```

Si **toutes ces vérifications passent** → ✅ Vous pouvez rendre le repo public en toute sécurité !

---

## 🆘 Besoin d'aide ?

- **Streamlit Discord** : [discuss.streamlit.io](https://discuss.streamlit.io)
- **Hugging Face Discord** : [hf.co/join/discord](https://hf.co/join/discord)

---

**Bonne chance ! 🚀**
