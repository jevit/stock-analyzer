# 🧭 Navigation Multi-Pages

L'application utilise maintenant le **système multi-pages natif de Streamlit**.

## ✅ Avantages

- ✅ **URLs fonctionnelles**: Vous pouvez accéder directement aux pages via l'URL
- ✅ **Navigation dans la sidebar**: Pages listées automatiquement dans la barre latérale
- ✅ **Bookmarks**: Mettez vos pages favorites en favoris
- ✅ **Partage facile**: Partagez des liens directs vers des pages spécifiques

## 📍 Pages disponibles

### 📊 Tableau de bord (Page principale)
**URL**: `http://localhost:8510/`

- Vue d'ensemble des signaux
- Tableau des opportunités
- Filtres et statistiques
- Export des données

### 🏆 Top Selections
**URL**: `http://localhost:8510/Top_Selections`

- Meilleurs actions par critères
- 7 onglets de classement:
  - 📊 Technique
  - 🚀 Momentum
  - 💎 Value
  - 📈 Growth
  - 💰 Dividendes
  - ⭐ Qualité
  - 🛡️ Défensif

### 📈 Backtesting
**URL**: `http://localhost:8510/Backtesting`

- Tester les stratégies sur données historiques
- Statistiques de performance
- Courbe d'équité
- Export des trades

### 🔔 Alertes
**URL**: `http://localhost:8510/Alertes`

- Configuration Email (Gmail, Outlook, etc.)
- Configuration Telegram
- Scanner automatique
- Historique des alertes

### 🔍 Detail
**URL**: `http://localhost:8510/Detail`

- Analyse détaillée d'un ticker
- Graphiques de prix et indicateurs
- Signaux détectés
- Niveaux techniques

## 🔧 Comment naviguer

### Méthode 1: Sidebar (Recommandé)
Utilisez les liens dans la **barre latérale gauche** de Streamlit:
- Les pages sont listées automatiquement
- Cliquez simplement sur la page désirée

### Méthode 2: URLs directes
Tapez directement l'URL dans votre navigateur:
```
http://localhost:8510/Top_Selections
http://localhost:8510/Backtesting
http://localhost:8510/Alertes
http://localhost:8510/Detail
```

### Méthode 3: Boutons dans les pages
Certains boutons dans l'interface changent automatiquement de page
(ex: "Voir détails →" dans le tableau de bord)

## 📝 Notes importantes

- **Chargez d'abord les données**: Sur la page principale, cliquez sur "🔄 Charger / Actualiser" avant d'explorer les autres pages
- **Session state partagé**: Les données chargées sont accessibles à toutes les pages
- **Page Detail**: Nécessite qu'un ticker soit sélectionné (cliquez sur "Voir détails" depuis le dashboard)

## 🆕 Nouveau vs Ancien système

### Ancien système (ne fonctionne plus):
❌ Navigation via boutons dans sidebar
❌ URLs ne fonctionnaient pas
❌ `st.session_state["page"] = "..."`

### Nouveau système (actuel):
✅ Navigation native Streamlit
✅ URLs fonctionnelles
✅ `st.switch_page(...)` pour navigation programmatique

---

**💡 Astuce**: Utilisez Ctrl+K (ou Cmd+K sur Mac) dans l'interface Streamlit pour ouvrir la palette de commandes et naviguer rapidement entre les pages !
