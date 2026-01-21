# Watchlists Thématiques

Ce dossier contient des watchlists organisées par thématique pour faciliter l'analyse sectorielle.

## 📁 Fichiers disponibles

### 🤖 Technologies Émergentes
- **tickers_ai_infrastructure.txt** - IA, datacenters, puces, serveurs (17 actions)
- **tickers_cloud_software.txt** - Cloud computing, SaaS avec IA (13 actions)
- **tickers_quantum.txt** - Quantum computing (5 actions)

### ⚡ Énergie & Transition
- **tickers_energy_ai.txt** - Uranium, nucléaire, électricité pour IA (9 actions)
- **tickers_renewables.txt** - Énergies renouvelables, solaire (7 actions)

### 🛡️ Sécurité & Défense
- **tickers_cybersecurity.txt** - Cybersécurité (8 actions)
- **tickers_defense.txt** - Aérospatial & défense US + Europe (16 actions)

### 🌏 Géographies
- **tickers_india.txt** - Actions indiennes (9 actions)
- **tickers_asia_pacific.txt** - Asie-Pacifique, Japon, Corée, Chine (15 actions)
- **tickers_europe_resilient.txt** - Actions européennes résilientes (50+ actions)

### 🧬 Santé & Bio
- **tickers_biotech.txt** - GLP-1, CRISPR, thérapies géniques (12 actions)

### 💰 Finance & Valeur
- **tickers_dividend_aristocrats.txt** - Dividend Aristocrats US (49 actions)
- **tickers_fintech.txt** - Paiements digitaux, fintech (9 actions)

### 🏗️ Matériaux & Infrastructure
- **tickers_materials.txt** - Lithium, cuivre, terres rares (9 actions)
- **tickers_infrastructure.txt** - Construction, matériaux (7 actions)
- **tickers_automation.txt** - Robotique, automation (7 actions)

## 💡 Comment utiliser

### Analyser une thématique spécifique

Vous pouvez créer une configuration personnalisée dans votre application pour charger uniquement certaines watchlists.

Par exemple, pour analyser uniquement l'IA:
```python
# Dans config/settings.py
WATCHLIST_FILE = "watchlists/tickers_ai_infrastructure.txt"
```

### Combiner plusieurs thématiques

Créez un fichier personnalisé qui combine plusieurs thématiques:
```bash
cat watchlists/tickers_ai_infrastructure.txt watchlists/tickers_energy_ai.txt > my_custom_watchlist.txt
```

### Analyser toutes les actions

Le fichier principal `tickers.txt` à la racine contient toutes les actions de toutes les thématiques.

## 📊 Statistiques

- **Total thématiques**: 16
- **Total actions uniques**: ~330+
- **Géographies couvertes**: US, Europe, Asie, Inde
- **Secteurs**: Tech, Santé, Énergie, Finance, Industrie, Défense

## ⚠️ Notes importantes

- Certains tickers peuvent ne pas être disponibles sur votre broker
- Les tickers asiatiques (.T, .KS, .HK, .NS) peuvent avoir des frais plus élevés
- Les tickers chinois (BABA, TCEHY) comportent un risque géopolitique
- Vérifiez toujours la disponibilité sur Saxo Bank avant d'investir

## 🔄 Mise à jour

Ces watchlists sont basées sur l'actualité de janvier 2025. Pensez à les mettre à jour régulièrement en fonction:
- De l'évolution du contexte géopolitique
- Des nouvelles tendances technologiques
- Des changements dans les Dividend Aristocrats
- De votre stratégie d'investissement personnelle
