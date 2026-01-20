# 🔔 Configuration des Alertes Automatiques

## 📧 Email (Recommandé - Plus simple)

### Configuration Gmail (5 minutes)

1. **Activez la validation en 2 étapes** (si pas déjà fait)
   - Allez sur https://myaccount.google.com/security
   - Activez "Validation en 2 étapes"

2. **Créez un mot de passe d'application**
   - Allez sur https://myaccount.google.com/apppasswords
   - Sélectionnez "Autre" comme nom d'application
   - Tapez "Stock Analyzer"
   - Cliquez sur **Générer**
   - **Copiez** le mot de passe de 16 caractères (ex: `abcd efgh ijkl mnop`)

3. **Modifiez le fichier `.env`** dans le dossier stock-analyzer :
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_FROM=votre.email@gmail.com
   EMAIL_PASSWORD=abcd efgh ijkl mnop
   EMAIL_TO=votre.email@gmail.com
   ```

4. **Testez la configuration**
   ```bash
   python scripts/test_email.py
   ```

   Vous devriez recevoir un email de test !

### Autres fournisseurs email

**Outlook/Hotmail:**
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_FROM=votre.email@outlook.com
EMAIL_PASSWORD=votre_mot_de_passe
EMAIL_TO=votre.email@outlook.com
```

**Yahoo:**
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
EMAIL_FROM=votre.email@yahoo.com
EMAIL_PASSWORD=mot_de_passe_app_yahoo
EMAIL_TO=votre.email@yahoo.com
```

---

## 📱 Telegram (Alternative)

1. **Créez un bot Telegram**
   - Ouvrez Telegram et cherchez `@BotFather`
   - Envoyez `/newbot`
   - Suivez les instructions
   - **Copiez le token** fourni

2. **Obtenez votre Chat ID**
   - Cherchez `@userinfobot` sur Telegram
   - Envoyez `/start`
   - **Copiez votre ID** (un nombre)

3. **Démarrez une conversation avec votre bot**
   - Cherchez votre bot par son nom
   - Cliquez sur START ou envoyez `/start`

4. **Modifiez le fichier `.env`**
   ```
   TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

5. **Testez**
   ```bash
   python scripts/test_telegram.py
   ```

---

## 🤖 Scanner Automatique

### Utilisation

**Test manuel:**
```bash
python scripts/auto_scanner.py --dry-run
```

**Scan réel:**
```bash
python scripts/auto_scanner.py --min-score 75
```

**Options:**
- `--min-score 75` : Score minimum pour alerter (défaut: 75)
- `--cooldown 24` : Heures avant de renvoyer la même alerte (défaut: 24)
- `--dry-run` : Tester sans envoyer d'alertes
- `--verbose` : Logs détaillés

### Planification automatique (Windows)

1. Ouvrez le **Planificateur de tâches** Windows
2. Cliquez sur **Créer une tâche de base**
3. Nom: "Stock Analyzer Scanner"
4. **Déclencheur**: Quotidien à 18h00 (après fermeture des marchés)
5. **Action**: Démarrer un programme
   - Programme: `python`
   - Arguments: `scripts\auto_scanner.py --min-score 75`
   - Démarrer dans: `C:\Perso\CurrentWorkspace-2\stock-analyzer`
6. Terminez l'assistant

### Planification automatique (Linux/Mac)

Éditez votre crontab:
```bash
crontab -e
```

Ajoutez cette ligne:
```
# Scan quotidien à 18h (jours de semaine)
0 18 * * 1-5 cd /chemin/vers/stock-analyzer && python scripts/auto_scanner.py
```

---

## 📊 Utilisation dans l'application

1. Lancez l'application:
   ```bash
   streamlit run app/main.py
   ```

2. Cliquez sur **🔔 Alertes** dans la barre latérale

3. **Configurez** Email ou Telegram

4. **Testez** la connexion

5. **Lancez** un scan manuel ou configurez le scan automatique

---

## ❓ Dépannage

### Email ne fonctionne pas

✅ Vérifiez que vous utilisez un **mot de passe d'application**, pas votre mot de passe Gmail normal

✅ Vérifiez que la validation en 2 étapes est **activée** sur votre compte Google

✅ Vérifiez qu'il n'y a **pas d'espaces** autour des valeurs dans le .env

✅ Vérifiez votre **connexion internet**

✅ Vérifiez vos **spam/courrier indésirable**

### Telegram ne fonctionne pas

✅ Assurez-vous d'avoir **démarré** une conversation avec votre bot (/start)

✅ Vérifiez que le **token** est correct (pas d'espaces)

✅ Vérifiez que le **Chat ID** est un nombre, pas un username

### Le scanner ne trouve aucun signal

C'est normal ! Les signaux techniques forts (score >= 75) ne sont pas présents tous les jours. Le scanner:
- Attend qu'un setup technique valide se forme
- Évite d'envoyer des doublons (même ticker/stratégie dans les 24h)
- N'envoie que si un **nouveau** signal fort apparaît

Vous pouvez:
- Baisser le `--min-score` pour voir plus de signaux
- Consulter le tableau de bord pour voir tous les scores
- Vérifier l'historique des alertes dans la page Alertes
