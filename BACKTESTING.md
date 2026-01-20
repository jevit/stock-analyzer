# 📈 Guide du Backtesting

## Qu'est-ce que le backtesting ?

Le backtesting consiste à **tester vos stratégies de trading sur les données historiques** pour voir comment elles auraient performé dans le passé.

C'est essentiel pour :
- ✅ **Valider** qu'une stratégie fonctionne vraiment
- 📊 **Mesurer** le taux de réussite et les gains/pertes moyens
- 🎯 **Comparer** différentes stratégies
- 💡 **Comprendre** les forces et faiblesses de chaque approche

---

## 🚀 Comment utiliser le backtesting

### 1. Chargez vos données
D'abord, allez sur le **Tableau de bord** et chargez votre watchlist.

### 2. Accédez à la page Backtesting
Cliquez sur **📈 Backtesting** dans la barre latérale.

### 3. Configurez les paramètres

**Période de test :**
- 90 jours (3 mois)
- 180 jours (6 mois)
- 365 jours (1 an) - **Recommandé**
- 730 jours (2 ans)

**Durée max de détention :**
- Combien de jours maximum tenir une position
- 30 jours par défaut (recommandé pour swing trading)

**Slippage :**
- Coût estimé d'entrée/sortie (spread, commissions)
- 0.1% par défaut

**Stratégie :**
- Toutes (teste les 3 stratégies)
- Trend Pullback
- Breakout
- Mean Reversion

### 4. Lancez le backtest
Cliquez sur **🚀 Lancer le Backtest**

⏱️ Cela peut prendre 1-2 minutes selon le nombre d'actions.

---

## 📊 Comprendre les résultats

### Métriques clés

**🎯 Taux de réussite (Win Rate)**
- Pourcentage de trades gagnants
- **Bon** : > 50%
- **Excellent** : > 60%

**📊 Gain moyen / Perte moyenne**
- Combien vous gagnez en moyenne par trade gagnant
- Combien vous perdez en moyenne par trade perdant
- **Important** : Le gain moyen doit être > perte moyenne

**💰 Profit Factor**
- Total des gains / Total des pertes
- **Bon** : > 1.5
- **Excellent** : > 2.0
- Si < 1.0 = Stratégie perdante globalement

**📈 Return total**
- Gain cumulé de tous les trades
- Exemple : +150% sur 1 an

**R/R moyen réalisé**
- Ratio Risk/Reward réellement obtenu
- **Bon** : > 1.5
- Idéalement proche du R/R théorique (2.0)

**Max Drawdown**
- Plus grosse baisse du capital
- Exemple : -25% = à un moment vous aviez perdu 25% par rapport au pic
- Plus c'est bas, mieux c'est

**Max pertes consécutives**
- Nombre maximum de trades perdants d'affilée
- Important pour le mental !

### Sorties

**🎯 Take Profit**
- Le trade a atteint l'objectif de gain
- **Bon signe** : beaucoup de TP = stratégie précise

**🛑 Stop Loss**
- Le trade a touché le stop loss
- Normal, fait partie du risk management

**⏱️ Timeout**
- Le trade n'a atteint ni le TP ni le SL avant la durée max
- Peut indiquer un setup qui manque de momentum

---

## 📈 Courbe d'équité

Le graphique montre l'**évolution du capital** au fil du temps.

**Bonne courbe** :
- ↗️ Tendance haussière régulière
- Peu de gros drawdowns

**Mauvaise courbe** :
- ↘️ Tendance baissière
- Volatilité excessive
- Gros drawdowns

---

## 🎯 Exemple de bons résultats

```
Stratégie: Breakout (365 jours)

🎯 Taux de réussite:     58.5%
📊 Gain moyen:          +9.2%
💰 Profit Factor:        2.1
📈 Return total:        +127%
⚖️ R/R moyen réalisé:   1.8
📉 Max Drawdown:        -18%
🛑 Max pertes consec:    4
```

**Analyse** :
- ✅ Win rate > 50%
- ✅ Profit factor > 2
- ✅ Bon return total
- ✅ R/R proche de 2
- ⚠️ Drawdown acceptable mais attention
- ✅ Pas trop de pertes consécutives

**Conclusion** : Stratégie solide et profitable

---

## ⚠️ Limitations du backtesting

Le backtesting est très utile mais a des limites :

1. **Le passé ne prédit pas l'avenir**
   - Ce qui a marché avant peut ne pas marcher demain

2. **Biais d'optimisation**
   - Ne pas sur-optimiser les paramètres pour "coller" au passé

3. **Conditions de marché changeantes**
   - Une stratégie peut marcher en marché haussier mais pas en baissier

4. **Slippage réel**
   - Le slippage réel peut être plus élevé que l'estimation

5. **Facteurs psychologiques**
   - En backtest, vous suivez parfaitement le plan
   - Dans la réalité, c'est plus difficile émotionnellement

---

## 💡 Conseils

✅ **Testez sur au moins 1 an de données**
✅ **Comparez plusieurs stratégies**
✅ **Vérifiez que le profit factor > 1.5**
✅ **Évaluez le max drawdown** (êtes-vous OK avec -20% ?)
✅ **Exportez les trades en CSV** pour analyse Excel
✅ **Combinez backtest + analyse fondamentale** pour les meilleurs résultats

❌ **N'utilisez PAS uniquement le backtest** pour décider
❌ **Ne sur-optimisez PAS** les paramètres
❌ **Ne négligez PAS** le risque et le money management

---

## 📥 Export des résultats

Cliquez sur **📥 Télécharger les trades (CSV)** pour obtenir un fichier Excel avec tous les trades.

Vous pouvez ensuite :
- Analyser dans Excel
- Filtrer par ticker
- Calculer vos propres statistiques
- Archiver les résultats

---

## 🎓 En résumé

Le backtesting vous permet de **valider vos stratégies** avant de trader avec de l'argent réel.

**Recherchez** :
- Win rate > 50%
- Profit factor > 1.5
- R/R réalisé proche de 2.0
- Drawdown acceptable pour vous
- Courbe d'équité haussière

**Rappelez-vous** : Le backtesting est un **outil d'aide à la décision**, pas une garantie de performance future !
