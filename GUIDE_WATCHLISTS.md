# Guide d'utilisation des Watchlists Thématiques

## 🎯 Switcher entre les watchlists

L'application dispose désormais d'un **sélecteur de watchlists** intégré dans la barre latérale.

### Méthode 1: Sélecteur dans l'interface (Recommandé)

1. Lancez l'application:
   ```bash
   python run_app.py
   ```

2. Dans la **barre latérale gauche**, sous la section "📁 Données", vous trouverez:
   - **Dropdown "🎯 Choisir une watchlist"** avec toutes les watchlists disponibles
   - Un compteur indiquant le nombre de tickers dans la liste sélectionnée

3. Sélectionnez la watchlist de votre choix dans le menu déroulant

4. Cliquez sur **"🔄 Charger / Actualiser"**

5. L'analyse se lance automatiquement pour tous les tickers de cette watchlist

### Méthode 2: Saisie manuelle

Si vous voulez analyser quelques tickers spécifiques sans charger une watchlist complète:

1. Dans la barre latérale, cliquez sur **"✍️ Saisie manuelle (optionnel)"**

2. Saisissez vos tickers (un par ligne):
   ```
   AAPL
   MSFT
   NVDA
   ```

3. Cliquez sur **"🔄 Charger / Actualiser"**

**Note**: La saisie manuelle a **priorité** sur la watchlist sélectionnée.

## 📂 Watchlists disponibles

### 📋 Watchlist Complète (principale)
La watchlist complète avec toutes les actions (~330+ tickers)

### Thématiques Technologiques
- **🤖 IA & Infrastructure**: Puces IA, datacenters, serveurs (17 actions)
- **☁️ Cloud & SaaS IA**: Cloud computing, SaaS avec IA (13 actions)
- **⚛️ Quantum Computing**: Informatique quantique (5 actions)

### Énergie & Transition
- **⚡ Énergie pour IA (Uranium, Nucléaire)**: Uranium, SMR, électricité (9 actions)
- **🌱 Énergies Renouvelables**: Solaire, éolien (7 actions)

### Sécurité & Défense
- **🛡️ Cybersécurité**: Protection cyber (8 actions)
- **🚀 Défense & Aérospatial**: Défense US + Europe (16 actions)

### Géographies
- **🇮🇳 Inde - Croissance**: Actions indiennes (9 actions)
- **🌏 Asie-Pacifique**: Japon, Corée, Chine, SEA (15 actions)
- **🇪🇺 Europe Résiliente**: Actions européennes défensives (50+ actions)

### Santé & Biotechnologie
- **🧬 Biotechnologie (GLP-1, CRISPR)**: Thérapies géniques, GLP-1 (12 actions)

### Finance & Valeur
- **💰 Dividend Aristocrats**: 25+ années de hausse dividendes (49 actions)
- **💳 Fintech & Paiements**: Paiements digitaux (9 actions)

### Matériaux & Infrastructure
- **⛏️ Matières Premières Critiques**: Lithium, cuivre, terres rares (9 actions)
- **🏗️ Infrastructure & Construction**: Construction, matériaux (7 actions)
- **🤖 Automatisation & Robotique**: Robotique, automation (7 actions)

### Opportunités à Fort Potentiel
- **💎 Small Caps Prometteuses**: Petites valorisations (<10B USD) dans secteurs prometteurs (130+ actions)

## 💡 Cas d'usage typiques

### Analyser un secteur spécifique

**Exemple**: Vous voulez analyser uniquement les actions liées à l'IA

1. Sélectionnez "🤖 IA & Infrastructure" dans le dropdown
2. Cliquez sur "🔄 Charger / Actualiser"
3. Résultat: Analyse de 17 actions IA (NVDA, AMD, AVGO, etc.)

### Comparer plusieurs thématiques

**Exemple**: Comparer les signaux dans les énergies renouvelables vs uranium

1. Chargez "🌱 Énergies Renouvelables"
2. Notez les signaux/scores
3. Revenez au sélecteur, choisissez "⚡ Énergie pour IA"
4. Rechargez et comparez

### Analyser votre watchlist personnelle

1. Créez un fichier texte dans `watchlists/` (ex: `ma_watchlist.txt`)
2. Ajoutez vos tickers (un par ligne)
3. Relancez l'app → votre fichier apparaîtra dans le dropdown

## 📊 Indicateur de watchlist active

Lorsque vous chargez une watchlist, un indicateur apparaît en haut du dashboard:

```
📂 Watchlist active: 🤖 IA & Infrastructure
```

Cela vous permet de toujours savoir quelle liste vous analysez.

## ⚡ Astuces

### Rafraîchir rapidement
- Cochez "Forcer le rafraîchissement" pour obtenir les dernières données du marché
- Sans cette option, les données en cache sont utilisées (plus rapide)

### Combiner des watchlists
Pour créer une watchlist personnalisée combinant plusieurs thématiques:

```bash
# Windows
type watchlists\tickers_ai_infrastructure.txt watchlists\tickers_energy_ai.txt > watchlists\ma_combo_ia_energie.txt

# Linux/Mac
cat watchlists/tickers_ai_infrastructure.txt watchlists/tickers_energy_ai.txt > watchlists/ma_combo_ia_energie.txt
```

### Utiliser les alertes avec une thématique

Pour recevoir des alertes Telegram uniquement pour une thématique:

1. Modifiez temporairement `tickers.txt` pour pointer vers votre watchlist:
   ```bash
   copy watchlists\tickers_small_caps_promising.txt tickers.txt
   ```

2. Lancez les alertes:
   ```bash
   python run_alerts.py --min-score 75
   ```

## ⚠️ Notes importantes

1. **Temps de chargement**: Plus une watchlist est grande, plus le premier chargement sera long
   - Small Caps (130+ tickers): ~10-15 min
   - IA & Infrastructure (17 tickers): ~2-3 min
   - Ensuite, le cache accélère tout

2. **Disponibilité sur Saxo Bank**: Certains tickers peuvent ne pas être disponibles
   - Tickers asiatiques (.T, .KS, .HK, .NS)
   - Small caps peu liquides
   - Vérifiez toujours avant d'investir

3. **Frais de trading**: Les frais varient selon le marché
   - Actions US: généralement les moins chères
   - Actions EU: frais modérés
   - Actions Asie: souvent plus élevés

## 🔄 Créer votre propre watchlist thématique

1. Créez un fichier dans `watchlists/` (ex: `tickers_mes_favoris.txt`)

2. Format du fichier:
   ```
   # Mon titre de watchlist

   ## Catégorie 1
   TICKER1
   TICKER2

   ## Catégorie 2
   TICKER3
   TICKER4
   ```

3. Pour qu'il apparaisse dans le dropdown, modifiez `src/utils/helpers.py`:
   ```python
   themed_lists = {
       # ... autres listes ...
       "tickers_mes_favoris.txt": "⭐ Mes Favoris",
   }
   ```

4. Relancez l'app → votre watchlist apparaît dans le sélecteur!

## 🆘 Support

Si vous avez des questions ou des problèmes:
- Consultez le `README.md` principal
- Vérifiez les logs dans `logs/errors.log`
- Testez avec une petite watchlist d'abord (ex: IA & Infrastructure)
