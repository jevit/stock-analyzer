"""
Tooltips et explications des termes techniques.
Centralise toutes les définitions pour cohérence.
"""

# ========================================
# INDICATEURS TECHNIQUES
# ========================================

TOOLTIPS = {
    # Moyennes mobiles
    "SMA20": """📈 **SMA20** (Simple Moving Average 20 jours)

Moyenne des prix des 20 derniers jours. Utilisée pour identifier la tendance court terme.
- Prix > SMA20 : Tendance court terme haussière
- Prix < SMA20 : Tendance court terme baissière""",

    "SMA50": """📈 **SMA50** (Simple Moving Average 50 jours)

Moyenne des prix des 50 derniers jours. Tendance moyen terme.
- Prix > SMA50 : Tendance moyen terme haussière
- Prix < SMA50 : Tendance moyen terme baissière
- Support/résistance dynamique important""",

    "SMA200": """📈 **SMA200** (Simple Moving Average 200 jours)

Moyenne des prix des 200 derniers jours. LA référence pour la tendance long terme.
- Prix > SMA200 : Tendance long terme haussière (marché haussier)
- Prix < SMA200 : Tendance long terme baissière (marché baissier)
- Niveau psychologique majeur pour les investisseurs""",

    # RSI
    "RSI": """⚡ **RSI** (Relative Strength Index)

Oscillateur de momentum mesurant la force/faiblesse du prix (0-100).

**Zones clés:**
- RSI > 70 : Surachat - Risque de correction
- RSI 50-70 : Momentum positif - Zone idéale pour acheter
- RSI 30-50 : Momentum faible
- RSI < 30 : Survente - Opportunité de rebond potentielle

**Interprétation:**
Un RSI élevé n'est pas forcément baissier ! En forte tendance haussière, le RSI peut rester >70 longtemps.""",

    # ATR
    "ATR": """🎢 **ATR** (Average True Range)

Mesure la volatilité moyenne du prix (en $ ou €).
Plus l'ATR est élevé, plus les mouvements de prix sont importants.

Utilisé pour:
- Dimensionner les stops loss (ex: stop à 2x ATR)
- Évaluer le risque
- Comparer la volatilité entre actions""",

    "ATR_PCT": """🎢 **ATR%** (ATR en pourcentage du prix)

ATR exprimé en % du prix actuel. Permet de comparer la volatilité entre actions de prix différents.

**Niveaux:**
- < 1.5% : Faible volatilité (action calme)
- 1.5-3% : Volatilité normale
- 3-5% : Volatilité élevée
- > 5% : Très volatile (risqué)""",

    # Bollinger Bands
    "BB": """📊 **Bandes de Bollinger**

Enveloppe statistique autour du prix (SMA ± 2 écarts-types).

**Utilisation:**
- Prix touche bande basse : Possibilité de rebond (survente)
- Prix touche bande haute : Possibilité de correction (surachat)
- Bandes serrées : Faible volatilité, breakout à venir
- Bandes larges : Forte volatilité

**BB Squeeze:** Quand les bandes sont très serrées, un mouvement explosif arrive souvent.""",

    # MACD
    "MACD": """🔄 **MACD** (Moving Average Convergence Divergence)

Indicateur de momentum qui suit la relation entre 2 moyennes mobiles exponentielles.

**Composants:**
- Ligne MACD : Différence entre EMA12 et EMA26
- Ligne Signal : EMA9 du MACD
- Histogramme : Différence MACD - Signal

**Signaux:**
- MACD croise au-dessus Signal : Signal haussier
- MACD croise en-dessous Signal : Signal baissier
- MACD > 0 : Momentum haussier
- MACD < 0 : Momentum baissier""",

    # Volume
    "VOLUME": """📊 **Volume**

Nombre de titres échangés pendant la période.

**Importance:**
Le volume CONFIRME la force d'un mouvement de prix.
- Hausse avec fort volume : Mouvement solide et durable
- Hausse avec faible volume : Mouvement faible, possiblement temporaire
- Volume inhabituel : Attention, événement important

**Volume Ratio:** Volume du jour / Moyenne 20 jours
- >2x : Explosion de volume (très fort intérêt)
- 1.5-2x : Volume élevé
- 0.8-1.5x : Normal
- <0.8x : Faible intérêt""",

    # Score
    "SCORE": """📊 **Score Global** (0-100)

Évaluation combinée de tous les indicateurs techniques pour cette stratégie.

**Barème:**
- 80-100 : Excellent - Signal très fort, conditions réunies
- 60-79 : Bon - Signal valide avec quelques réserves
- 40-59 : Moyen - Setup en développement
- 0-39 : Faible - Conditions non favorables

Le score prend en compte: tendance, momentum, volume, volatilité, et critères spécifiques à chaque stratégie.""",

    # Risk/Reward
    "RR": """💰 **R/R** (Risk/Reward Ratio)

Rapport Gain potentiel / Risque pris.

**Exemple:** R/R de 2:1 signifie :
- Si vous risquez 100€ (distance au stop loss)
- Vous visez un gain de 200€ (distance à l'objectif)

**Règle d'or:**
Toujours viser un R/R minimum de 2:1, idéalement 3:1 ou plus.
Même avec 50% de réussite, un R/R de 2:1 vous rend profitable !""",

    # Niveaux techniques
    "ENTRY": """🎯 **Niveau d'entrée**

Prix conseillé pour entrer en position. Généralement proche du cours actuel.

**Note:** Ce niveau est **indicatif** et non un conseil d'investissement.
Validez toujours avec votre propre analyse.""",

    "STOP_LOSS": """🛑 **Stop Loss** (Invalidation)

Niveau où couper la position si le scénario ne se réalise pas.

**Pourquoi c'est crucial:**
- Limite vos pertes
- Protège votre capital
- Permet de rester objectif (pas d'émotions)

**Règle:** TOUJOURS placer un stop loss AVANT d'entrer en position !""",

    "TAKE_PROFIT": """🎯 **Take Profit** (Objectif)

Niveau où prendre vos bénéfices si le scénario se réalise.

**Stratégies:**
- Prendre 50% à l'objectif, laisser courir le reste
- Sortir totalement à l'objectif
- Utiliser un trailing stop pour suivre le mouvement

Ne soyez pas trop gourmand ! Un profit réalisé est toujours mieux qu'un profit papier.""",

    # Stratégies
    "TREND_PULLBACK": """📈 **Trend Pullback**

Stratégie : Acheter une correction temporaire dans une tendance haussière établie.

**Logique:**
"Acheter la baisse dans une tendance forte"

**Conditions:**
- Tendance haussière confirmée (prix > SMA200)
- Prix revient vers SMA50 (repli sain)
- RSI remonte au-dessus de 50
- Volume présent

**Idéal pour:** Swing trading moyen terme (plusieurs semaines)""",

    "BREAKOUT": """🚀 **Breakout**

Stratégie : Acheter quand le prix casse une résistance importante avec volume.

**Logique:**
"Le prix casse un niveau clé = nouvelle impulsion haussière"

**Conditions:**
- Prix casse le plus haut de 55 jours
- Volume élevé (confirmation)
- Tendance haussière
- Momentum fort

**Idéal pour:** Capter les nouvelles impulsions, trading court/moyen terme""",

    "MEAN_REVERSION": """↩️ **Mean Reversion**

Stratégie : Acheter un rebond après une chute excessive (survente).

**Logique:**
"Ce qui monte redescend, ce qui descend remonte"

**Conditions:**
- Prix touche la bande de Bollinger basse
- RSI en survente (<30)
- Première chandelier de rebond
- Tendance globale haussière

**Idéal pour:** Trading court terme, actions volatiles
**Risque:** Essayer de "attraper un couteau qui tombe" - attend confirmation !""",

    "MACD_CROSSOVER": """🔄 **MACD Crossover**

Stratégie : Acheter quand le MACD croise sa ligne de signal vers le haut.

**Logique:**
"Changement de momentum = début d'un nouveau mouvement"

**Conditions:**
- MACD croise au-dessus de sa Signal (croisement haussier)
- Prix au-dessus SMA200 (tendance haussière)
- RSI 50-70 (momentum positif)
- Volatilité normale

**Idéal pour:** Détecter les changements de momentum, trading moyen terme""",

    "GOLDEN_CROSS": """⭐ **Golden Cross**

Stratégie : Signal long terme MAJEUR - SMA50 croise SMA200 vers le haut.

**Logique:**
"Confirmation d'un changement de tendance structurel"

**Conditions:**
- SMA50 croise au-dessus SMA200 (rare !)
- Prix au-dessus des 2 SMAs
- Volume de confirmation
- RSI montrant de la force

**Idéal pour:** Investissement long terme, buy & hold
**Fréquence:** Très rare (quelques fois par an max)
**Note:** Signal très fiable historiquement mais arrive souvent tard""",

    "VOLUME_BREAKOUT": """📊 **Volume Breakout**

Stratégie : Breakout de prix + EXPLOSION de volume = mouvement puissant.

**Logique:**
"Volume massif = argent institutionnel = mouvement fort et durable"

**Conditions:**
- Prix casse le plus haut 20 jours
- Volume >2x la moyenne (CRITÈRE CLÉ)
- RSI >60 (momentum)
- Tendance haussière

**Idéal pour:** Capter les mouvements explosifs, court terme
**Avantage:** Le volume confirme la cassure (pas un faux signal)""",
}


def get_tooltip(key: str) -> str:
    """
    Récupère le tooltip pour une clé donnée.

    Args:
        key: Clé du terme technique

    Returns:
        Texte du tooltip ou chaîne vide
    """
    return TOOLTIPS.get(key.upper(), "")
