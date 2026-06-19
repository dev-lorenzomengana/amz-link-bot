# 🤖 @personal_affiliate_amazon_bot

Bot Telegram per convertire link Amazon in link affiliati personalizzati. Ogni utente imposta il proprio tag Amazon e il bot risponde con link affiliati pronti da condividere.

## ✅ Il bot è online
Telegram: @personal_affiliate_amazon_bot

## Cosa fa
- Convertisce link Amazon con il tuo tag affiliato
- Supporta link normali e corti `amzn.to`, `a.co`, `amzn.eu`
- Funziona inline in qualsiasi chat
- Gestisce un tag affiliato diverso per ogni utente
- Supporta domini Amazon internazionali

## Avvio rapido
```bash
pip install -r requirements.txt
python setup.py
python main.py
```

## Comandi principali
- `/start` — avvia il bot
- `/settag <tag>` — imposta il tuo tag affiliato
- `/help` — aiuto
- `/export` — esporta i tuoi dati
- `/deletedata` — elimina i tuoi dati

## Uso
1. Apri Telegram
2. Avvia @personal_affiliate_amazon_bot
3. Invia `/settag nome-tag`
4. Invia un link Amazon e ricevi il link affiliato

## Inline
Usa il bot in qualsiasi chat con:

`@personal_affiliate_amazon_bot https://amazon.it/dp/B08N5WRWNW`

Il bot fornisce il link convertito direttamente nella chat.

```
👤 Utente: Guarda questo prodotto!
          https://amazon.it/dp/B08N5WRWNW

🤖 Bot: ✅ Link convertito con il tuo tag!
        
        Guarda questo prodotto!
        https://www.amazon.it/dp/B08N5WRWNW?tag=mybrand-21
        
        🔗 Link Amazon convertito con successo!
        Tag utilizzato: mybrand-21
        💰 Ora guadagni commissioni su ogni acquisto!
```

### Gestione Impostazioni
```
👤 Utente: /settings

🤖 Bot: ⚙️ Le tue Impostazioni
        
        👤 Account: ✅ Configurato
        Tag affiliato: mybrand-21
        Membro dal: 15/01/2024
        
        📊 Statistiche:
        Link convertiti: 127
        
        🔧 Usa /settag per cambiare tag
```

## 🔧 Sviluppo e Test

### Struttura del Progetto
```
_botTelegram/
├── main.py              # Bot principale con gestione personalizzata
├── amazon_processor.py  # Logica conversione link Amazon + risoluzione short link
├── user_manager.py      # Gestione utenti e configurazioni (save atomico)
├── product_info.py      # Arricchimento prodotto opzionale via PA-API
├── test_processor.py    # Test completi del sistema
├── setup.py            # Setup guidato del bot
├── requirements.txt    # Dipendenze Python
├── .env.example       # Template configurazione admin
├── .env               # Configurazione (gitignored)
├── .gitignore         # File da escludere
├── user_data.json     # Dati utenti (creato automaticamente)
└── README.md          # Questa guida
```

### Test del Sistema
```bash
# Test completo (processore + gestione utenti)
python test_processor.py

# Test specifico processore Amazon
python -c "
from amazon_processor import AmazonLinkProcessor
processor = AmazonLinkProcessor('test-tag')
print(processor.create_affiliate_link('https://amazon.it/dp/B08N5WRWNW'))
"
```

### Test Utente Singolo
Il nuovo script di test include:
- Test validazione tag affiliato
- Test workflow completo utente
- Test statistiche personali
- Test interattivo con simulazione utente

## 📊 Monitoraggio

### Log del Sistema
Il bot produce log dettagliati:
```
INFO - Avvio bot Amazon Affiliate (Personalizzato)
INFO - Utenti totali: 45, Configurati: 38
INFO - Utente 123456 (Mario): convertiti 2 link con tag mario-shop
```

### Statistiche Admin (`/stats`)
```
📊 Statistiche Bot Admin

👥 Utenti:
• Totale utenti: 45
• Utenti configurati: 38  
• Utenti non configurati: 7
• Attivi ultimi 7 giorni: 23

📈 Conversioni:
• Link convertiti totali: 1,247
• Media per utente: 27.7

🔧 Sistema: ✅ Operativo
```

### Statistiche Utente (`/mystats`)
Ogni utente vede solo le proprie:
```
📊 Le tue Statistiche

👤 Tag affiliato: mario-shop
📈 Link convertiti: 42
🗓️ Ultima attività: Oggi alle 15:30
```

## 🚀 Deploy in Produzione

### Hosting Consigliati
1. **VPS/Server** - Controllo totale
2. **Railway** - Deploy moderno e semplice
3. **Heroku** - Gratuito/economico
4. **PythonAnywhere** - Specializzato Python

### Deploy su Heroku
```bash
# Crea Procfile
echo "worker: python main.py" > Procfile

# Deploy
git init
git add .
git commit -m "Bot personalizzato"
heroku create my-affiliate-bot
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set ADMIN_IDS=your_admin_id
git push heroku main
heroku ps:scale worker=1
```

### Deploy su Railway
1. Connetti repository GitHub
2. Configura variabili ambiente
3. Deploy automatico

### Backup Dati Utenti
```bash
# Backup manuale
cp user_data.json backup/user_data_$(date +%Y%m%d).json

# Script di backup automatico (cron)
0 2 * * * cp /path/to/bot/user_data.json /backup/user_data_$(date +\%Y\%m\%d).json
```

## 🛡️ Sicurezza e Privacy

### Protezione Dati
- ✅ Dati utente criptati in memoria
- ✅ File `.env` escluso da versioning  
- ✅ Backup sicuri dei dati utenti
- ✅ Validazione rigorosa input tag

### GDPR Compliance
- ✅ Comando `/deletedata` per eliminazione
- ✅ Dati minimi necessari (solo tag + statistiche)
- ✅ Consenso esplicito per configurazione
- ✅ Trasparenza su utilizzo dati

### Best Practices
```bash
# Permessi file dati
chmod 600 user_data.json

# Rotazione log
logrotate.d/amazon_bot

# Monitoraggio uptime
systemctl enable amazon-bot
systemctl start amazon-bot
```

## 🐛 Troubleshooting

### Problemi Comuni

**Bot non risponde**
```bash
# Verifica processo
ps aux | grep python | grep main.py

# Controlla log
tail -f bot.log

# Testa token
python -c "import requests; print(requests.get('https://api.telegram.org/bot<TOKEN>/getMe').json())"
```

**Utente non può configurare tag**
- Verifica formato tag (3-50 caratteri, solo alfanumerici e trattini)
- Controlla che il tag non inizi/finisci con trattino
- Vedi log per errori di validazione

**Link non convertiti**
- Assicurati che siano link Amazon validi
- Verifica che l'utente abbia configurato il tag
- Controlla domini supportati

**Dati utente persi**
- Verifica che `user_data.json` non sia stato eliminato
- Controlla backup in cartella `backup/`
- Verifica permessi di scrittura file

### Log di Debug
```python
# Per debug avanzato, modifica main.py
logging.getLogger().setLevel(logging.DEBUG)
```

## 🤝 Contributi e Supporto

### Contribuire
1. Fork il repository
2. Crea branch feature (`git checkout -b feature/nuova-funzionalita`)
3. Commit modifiche (`git commit -m 'Aggiunge nuova funzionalità'`)
4. Push branch (`git push origin feature/nuova-funzionalita`)  
5. Apri Pull Request

### Funzionalità Future
- [x] Risoluzione link corti (amzn.to, a.co, amzn.eu)
- [x] Modalità inline in qualsiasi chat
- [x] Esportazione dati GDPR (`/export`)
- [x] Info prodotto opzionale via PA-API
- [ ] Supporto link affiliati multipli (non solo Amazon)
- [ ] Dashboard web per statistiche avanzate
- [ ] Integrazione con Google Analytics
- [ ] Sistema di referral tra utenti
- [ ] API REST per integrazioni esterne
- [ ] Bot multi-lingua

### Supporto
- 💬 Apri issue su GitHub per bug/richieste
- 📧 Contatta sviluppatori per supporto enterprise
- 📖 Consulta documentazione API Telegram Bot

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

---

**🎉 Bot Personalizzato - Ogni Utente il Proprio Tag! 💰**

*Massimizza le commissioni affiliate con gestione utenti avanzata.*