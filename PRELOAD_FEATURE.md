# 🚀 Préchargement Automatique - Nouvelle Fonctionnalité

## Qu'est-ce que c'est ?

L'application **charge automatiquement** une petite liste d'actions au premier démarrage si le cache est vide.

---

## 📋 Comment ça marche ?

### Au premier démarrage

1. **L'app détecte** que le cache est vide
2. **Affiche un message** : "🚀 Premier démarrage détecté ! Chargement d'une liste d'exemple..."
3. **Charge automatiquement** 7 actions populaires :
   - AAPL (Apple)
   - MSFT (Microsoft)
   - GOOGL (Alphabet)
   - NVDA (NVIDIA)
   - TSLA (Tesla)
   - META (Meta/Facebook)
   - AMZN (Amazon)
4. **Affiche le dashboard** avec ces données

### Aux démarrages suivants

- ✅ **Ne se redéclenche pas** (déjà des données en cache)
- ✅ Vous pouvez charger votre propre liste à tout moment
- ✅ Le cache se remplit progressivement avec vos choix

---

## 🎯 Avantages

### Pour les nouveaux utilisateurs
- ✅ **Pas d'écran vide** au premier lancement
- ✅ **Découverte immédiate** des fonctionnalités
- ✅ **Comprend comment ça marche** avant de charger sa propre liste

### Pour Streamlit Cloud
- ✅ **Démonstration instantanée** de l'app
- ✅ Les visiteurs voient directement l'interface avec des données
- ✅ Meilleure première impression

---

## ⚙️ Comportement technique

### Conditions de déclenchement

Le préchargement se déclenche **uniquement si** :
1. ❌ Aucune donnée n'est chargée (`data_loaded = False`)
2. ❌ Le cache est **complètement vide** (0 tickers)
3. ❌ Le préchargement n'a **pas déjà été tenté** cette session

### Sécurité

- 🔒 **Une seule tentative** par session (évite les boucles)
- 🔒 **Gestion d'erreur** : si le préchargement échoue, l'app continue normalement
- 🔒 **Non-intrusif** : vous pouvez immédiatement charger votre propre liste

---

## 🎨 Expérience utilisateur

### Avant (sans préchargement)
```
┌─────────────────────────────┐
│ Bienvenue !                 │
│                             │
│ Pour commencer:             │
│ 1. Créez tickers.txt        │
│ 2. Chargez vos données      │
│                             │
│ [Analyser exemple]          │
└─────────────────────────────┘
```
→ Écran vide, utilisateur doit cliquer

### Après (avec préchargement)
```
┌─────────────────────────────┐
│ 🚀 Premier démarrage !      │
│ Chargement automatique...   │
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│ ✅ 7 actions chargées !     │
│                             │
│ 📊 Dashboard avec données   │
│ - AAPL: Score 75            │
│ - MSFT: Score 68            │
│ ...                         │
└─────────────────────────────┘
```
→ Dashboard directement visible !

---

## 🔧 Configuration

### Modifier la liste préchargée

Éditez `app/main.py`, fonction `auto_preload_data()` :

```python
# Ligne ~262
default_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN"]
```

**Recommandations** :
- ✅ Gardez 5-10 tickers (rapide à charger)
- ✅ Choisissez des actions **liquides** (évite les erreurs)
- ✅ Choisissez des actions **populaires** (tout le monde connaît)
- ❌ Évitez trop de tickers (ralentit le démarrage)

### Désactiver le préchargement

Commentez simplement l'appel dans `main()` :

```python
# Ligne ~301
# Auto-preload data on first run if cache is empty
# if auto_preload_data():
#     st.rerun()
```

---

## 📊 Impact sur les performances

### Temps de chargement

**Premier démarrage (cache vide)** :
- Sans préchargement : ~1 seconde (affichage page)
- Avec préchargement : ~5-10 secondes (téléchargement + analyse)

**Démarrages suivants** :
- Identique : ~1 seconde (données en cache)

### Utilisation réseau

- 7 tickers × ~500 jours de données historiques
- ~1-2 MB de téléchargement (yfinance)
- Se fait **une seule fois** (ensuite tout est en cache)

---

## 🐛 Dépannage

### Le préchargement ne se déclenche pas

**Cause** : Des données sont déjà en cache

**Solution** :
1. Videz le cache via l'interface (sidebar → "Vider le cache")
2. Ou supprimez `data/cache/`
3. Rechargez l'app

### Le préchargement échoue

**Cause possible** : Problème réseau avec yfinance

**Solution** :
- L'app continue normalement
- Un message s'affiche : "⚠️ Le préchargement automatique a échoué"
- Chargez manuellement vos tickers

### Je veux changer la liste préchargée

**Éditez** `app/main.py` ligne ~262 :

```python
# Exemple : Actions françaises
default_tickers = ["MC.PA", "OR.PA", "AIR.PA", "SAN.PA"]

# Exemple : ETFs
default_tickers = ["SPY", "QQQ", "IWM", "DIA"]

# Exemple : Crypto-related
default_tickers = ["COIN", "MSTR", "RIOT", "MARA"]
```

---

## ✅ Recommandation

**Gardez cette fonctionnalité activée** si :
- ✅ Vous déployez sur Streamlit Cloud (démo publique)
- ✅ Vous voulez impressionner les visiteurs
- ✅ Vous voulez une meilleure UX

**Désactivez-la** si :
- ❌ Vous voulez un démarrage ultra-rapide
- ❌ Vous avez des limitations réseau strictes
- ❌ Vous préférez toujours partir d'un écran vide

---

## 🎉 Résumé

**Avant** : Écran vide → Utilisateur doit agir → Voir les données

**Après** : Démarrage → **Données automatiques** → Dashboard directement !

Une petite amélioration qui fait une **grande différence** pour l'expérience utilisateur ! 🚀

---

*Cette fonctionnalité a été ajoutée pour améliorer l'expérience du premier démarrage.*
