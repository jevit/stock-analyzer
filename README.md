# Stock Analyzer 📊

Application personnelle d'analyse technique boursière. Détecte des setups techniques prédéfinis sur une watchlist et génère des alertes.

> ⚠️ **Avertissement Important**: Cette application fournit uniquement une analyse technique à des fins éducatives et personnelles. Elle ne constitue en aucun cas un conseil en investissement. Toute décision d'investissement reste de votre entière responsabilité.

## Fonctionnalités

- **Import watchlist** depuis un fichier texte
- **Téléchargement automatique** des données via yfinance (gratuit)
- **Calcul d'indicateurs techniques**:
  - SMA 20, 50, 200
  - RSI (14)
  - ATR (14) et ATR%
  - Bollinger Bands (20, 2)
  - Volume moyen 20 jours
- **Détection de 3 stratégies**:
  - **Trend Pullback**: Repli vers SMA50 en tendance haussière
  - **Breakout**: Cassure des plus hauts 55 jours avec volume
  - **Mean Reversion**: Rebond depuis survente (BB + RSI)
- **Scoring** 0-100 avec bonus pour signaux multiples
- **Interface Streamlit** avec dashboard et vue détaillée
- **Export CSV** des résultats
- **Alertes Telegram** optionnelles
- **Cache local** pour éviter les retéléchargements

## Installation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner ou télécharger** le projet

2. **Créer un environnement virtuel** (recommandé):
```bash
cd stock-analyzer
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

4. **Configurer la watchlist**:
Éditez le fichier `tickers.txt` avec vos tickers (un par ligne):
```
AAPL
MSFT
GOOGL
```

5. **(Optionnel) Configurer Telegram**:
Copiez `.env.example` vers `.env` et renseignez vos identifiants (voir section Telegram ci-dessous).

## Utilisation

### Lancer l'application web

```bash
python run_app.py
```

Ou directement avec Streamlit:
```bash
streamlit run app/main.py
```

L'application s'ouvre dans votre navigateur à l'adresse `http://localhost:8501`.

### Lancer les alertes quotidiennes

```bash
# Analyse et envoi d'alertes Telegram
python run_alerts.py

# Avec options
python run_alerts.py --min-score 80 --force-refresh

# Tester la connexion Telegram
python run_alerts.py --test
```

### Programmer les alertes (Windows)

Utilisez le Planificateur de tâches Windows:
1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. Définir le déclencheur (ex: tous les jours à 18h)
4. Action: Démarrer un programme
5. Programme: `C:\chemin\vers\venv\Scripts\python.exe`
6. Arguments: `C:\chemin\vers\stock-analyzer\run_alerts.py`

## Configuration Telegram

### Créer un bot Telegram

1. Ouvrir Telegram et chercher `@BotFather`
2. Envoyer `/newbot`
3. Donner un nom à votre bot (ex: "Mon Stock Analyzer")
4. Donner un username (ex: "mon_stock_analyzer_bot")
5. **Copier le token** fourni par BotFather

### Obtenir votre Chat ID

1. Chercher `@userinfobot` sur Telegram
2. Envoyer `/start`
3. **Copier votre Chat ID** (nombre)

### Configurer l'application

1. Copier `.env.example` vers `.env`:
```bash
cp .env.example .env
```

2. Éditer `.env` avec vos valeurs:
```
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

3. Tester la connexion:
```bash
python run_alerts.py --test
```

## Structure du projet

```
stock-analyzer/
├── app/                      # Application Streamlit
│   ├── main.py              # Point d'entrée
│   ├── pages/               # Pages de l'app
│   │   ├── dashboard.py     # Tableau de bord
│   │   └── detail.py        # Vue détaillée
│   └── components/          # Composants UI
│       ├── charts.py        # Graphiques Plotly
│       └── tables.py        # Tableaux
├── src/                      # Modules métier
│   ├── data/                # Téléchargement et cache
│   │   ├── downloader.py
│   │   └── cache.py
│   ├── indicators/          # Calcul indicateurs
│   │   └── technical.py
│   ├── strategies/          # Stratégies de détection
│   │   ├── base.py
│   │   ├── trend_pullback.py
│   │   ├── breakout.py
│   │   └── mean_reversion.py
│   ├── scoring/             # Système de scoring
│   │   └── scorer.py
│   ├── alerts/              # Alertes Telegram
│   │   └── telegram.py
│   └── utils/               # Utilitaires
│       └── helpers.py
├── config/                   # Configuration
│   └── settings.py
├── data/
│   └── cache/               # Cache des données (auto-généré)
├── tickers.txt              # Votre watchlist
├── requirements.txt         # Dépendances Python
├── run_app.py              # Script lancement app
├── run_alerts.py           # Script alertes
├── .env.example            # Template config Telegram
└── README.md
```

## Stratégies détaillées

### Trend Pullback
Détecte les replis vers la moyenne mobile dans une tendance établie.

**Conditions**:
- Prix > SMA200 (tendance haussière)
- Prix proche de SMA50 (< 2% de distance)
- RSI croise 50 à la hausse (sur 3 jours)
- Volume du jour > moyenne 20 jours

**Pondération du score**:
- Tendance haussière: 25 pts
- Proximité SMA50: 10-25 pts (selon distance)
- RSI momentum: 0-25 pts
- Volume: 0-25 pts

### Breakout
Détecte les cassures de résistance avec confirmation de volume.

**Conditions**:
- Prix > plus haut 55 jours
- Volume > 1.5x moyenne 20 jours
- ATR% > 1% (évite les actions "plates")

**Pondération du score**:
- Cassure: 25-35 pts (selon force)
- Volume: 0-35 pts
- Volatilité: 0-20 pts
- Bonus tendance: +10 pts si > SMA200

### Mean Reversion
Détecte les situations de survente avec potentiel de rebond.

**Conditions**:
- Prix < Bollinger Band basse (ou récemment)
- RSI < 30 (ou récemment)
- Signal de retour: prix repasse au-dessus de BB basse

**Pondération du score**:
- Survente BB: 0-30 pts
- Survente RSI: 0-30 pts
- Signal de rebond: 0-25 pts
- Volume: 5-15 pts
- Bonus tendance: +10 pts si > SMA200

### Score global
- Score global = max(scores stratégies)
- Bonus +10 si 2 stratégies en signal
- Bonus +15 si 3 stratégies en signal
- Maximum: 100

## Niveaux techniques

Les niveaux affichés sont **purement indicatifs** et basés sur l'ATR:

- **Entrée théorique**: Prix actuel
- **Invalidation**: Prix - 2×ATR (ou 2.5×ATR pour breakout)
- **Objectif**: Prix + 2×ATR (ou 3×ATR pour breakout)
- **R/R**: Ratio Reward/Risk

## Cache

Les données sont mises en cache localement au format Parquet pour éviter les retéléchargements.

- **Emplacement**: `data/cache/`
- **Expiration**: 12 heures par défaut
- **Forcer le rafraîchissement**: Option dans l'interface ou `--force-refresh`

## Limitations

- Données journalières uniquement (pas de temps réel)
- Source: yfinance (gratuit mais peut avoir des limitations)
- Analyse purement technique (pas de fondamentaux)
- Pas de backtesting intégré

## Dépannage

### "No data returned for ticker"
- Vérifiez que le ticker existe (format US: AAPL, pas AAPL.PA)
- yfinance peut avoir des limitations temporaires

### "Telegram not configured"
- Vérifiez que `.env` existe et contient les bonnes valeurs
- Testez avec `python run_alerts.py --test`

### Cache corrompu
- Videz le cache via l'interface ou supprimez `data/cache/`

## Licence

Usage personnel uniquement. Pas de redistribution commerciale.

---

*Développé avec Python, Streamlit et yfinance.*
