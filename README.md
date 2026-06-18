# 🤖 Bot Telegram Amazon Affiliate Personalizzato

Un bot Telegram intelligente che permette a **ogni utente** di configurare il proprio tag affiliato Amazon personale. Ogni utente converte i link Amazon con il proprio tag affiliato individuale!

## ✨ Caratteristiche Principali

- 👥 **Tag affiliato personale**: Ogni utente configura il proprio tag Amazon
- 🔗 **Conversione automatica**: Rileva e converte automaticamente tutti i link Amazon  
- 🩳 **Link corti risolti**: `amzn.to`, `a.co`, `amzn.eu` vengono seguiti e convertiti davvero
- ⚡ **Modalità inline**: usa `@nomebot <link>` in qualsiasi chat Telegram
- 🌍 **Supporto internazionale**: Funziona con tutti i domini Amazon mondiali
- 🎯 **Mantiene localizzazione**: Preserva il dominio originale del link
- 🛍️ **Info prodotto (opzionale)**: titolo/prezzo/immagine via PA-API se hai le chiavi
- 📊 **Statistiche personali**: Ogni utente ha le proprie statistiche di conversione
- 📱 **Interfaccia intuitiva**: Configurazione semplice e comandi chiari
- 🔒 **Privacy**: Ogni utente gestisce solo i propri dati
- 🛡️ **GDPR compliance**: esporta (`/export`) o elimina (`/deletedata`) i tuoi dati

## 🚀 Setup Bot (Per Amministratori)

### 1. Prerequisiti
- Python 3.8+
- Account Telegram  
- Token bot da @BotFather

### 2. Installazione Rapida
```bash
# Installa dipendenze
pip install -r requirements.txt

# Configurazione automatica
python setup.py

# Avvia il bot
python main.py
```

### 3. Configurazione Manuale
```bash
# Copia il template di configurazione
cp .env.example .env
```

Modifica il file `.env`:
```env
# Solo il token del bot è necessario per l'admin
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# ID admin (per statistiche globali) 
ADMIN_IDS=123456789,987654321
```

## 👤 Come Usarlo (Per Utenti)

### Prima Configurazione
1. **Apri il bot** su Telegram
2. **Invia `/start`** - Il bot ti guiderà
3. **Configura il tuo tag**: `/settag il-tuo-tag-affiliato`

**Esempio:**
```
/settag mytag-21
```

### Utilizzo Quotidiano
1. **Invia un link Amazon** in chat
2. **Ricevi il link convertito** con il tuo tag
3. **Condividi e guadagna** commissioni!

**Esempio:**
```
Tu: https://amazon.it/dp/B08N5WRWNW

Bot: ✅ Link convertito con il tuo tag!
     https://www.amazon.it/dp/B08N5WRWNW?tag=mytag-21
## 💬 Comandi Disponibili

### 🚀 Configurazione
- `/start` - Messaggio di benvenuto e guida iniziale
- `/settag <tag>` - Configura il tuo tag affiliato Amazon
- `/setup <tag>` - Alias per `/settag`

### ⚙️ Gestione Account
- `/settings` - Visualizza e gestisci le tue impostazioni
- `/config` - Alias per `/settings`  
- `/mystats` - Le tue statistiche personali di conversione
- `/export` - Esporta tutti i tuoi dati in JSON (GDPR)
- `/deletedata` - Elimina tutti i tuoi dati (GDPR)

### ⚡ Modalità Inline
In **qualsiasi** chat (anche con amici, senza aprire il bot) scrivi:
```
@nomebot https://amazon.it/dp/B08N5WRWNW
```
e seleziona il risultato per inviare il link già affiliato.

> **Va abilitata una volta sola** lato BotFather: apri [@BotFather](https://t.me/BotFather) → `/setinline` → scegli il bot → imposta un testo placeholder (es. "Incolla un link Amazon").

### 📚 Aiuto
- `/help` - Guida completa all'utilizzo

### 👑 Admin (Solo Amministratori)
- `/stats` - Statistiche globali del bot

## 🛠️ Come Ottenere il Tag Affiliato Amazon

### 1. Registrati ad Amazon Associates
- Vai su [Amazon Associates](https://affiliate-program.amazon.com/)
- Crea un account o accedi
- Completa la registrazione

### 2. Trova il Tuo Tag
- Nel dashboard troverai il tuo **Associate Tag**
- Formato tipico: `nome-tag-21` 
- Usa **solo** la parte prima del trattino: `nome-tag`

### 3. Configura nel Bot
```
/settag nome-tag
```

## 📊 Domini Amazon Supportati

- amazon.com (USA) 🇺🇸
- amazon.it (Italia) 🇮🇹  
- amazon.co.uk (Regno Unito) 🇬🇧
- amazon.de (Germania) 🇩🇪
- amazon.fr (Francia) 🇫🇷
- amazon.es (Spagna) 🇪🇸
- amazon.ca (Canada) 🇨🇦
- amazon.com.au (Australia) 🇦🇺
- amazon.co.jp (Giappone) 🇯🇵
- amazon.in (India) 🇮🇳
- amazon.com.br (Brasile) 🇧🇷
- amazon.com.mx (Messico) 🇲🇽
- amzn.to (link corti Amazon)
- amzn.eu (link corti europei)
- a.co (link corti USA)

## 🔧 Configurazione Avanzata

### Variabili d'Ambiente (Admin)

| Variabile | Descrizione | Obbligatorio | Esempio |
|-----------|-------------|--------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot Telegram | ✅ | `123456789:ABCdef...` |
| `ADMIN_IDS` | ID Telegram degli admin | ❌ | `123456789,987654321` |
| `PAAPI_ACCESS_KEY` | Chiave PA-API (info prodotto) | ❌ | `AKIA...` |
| `PAAPI_SECRET_KEY` | Secret PA-API | ❌ | `...` |
| `PAAPI_PARTNER_TAG` | Partner tag PA-API | ❌ | `mytag-21` |
| `PAAPI_COUNTRY` | Paese PA-API di default | ❌ | `IT` |

**Nota**: Il tag affiliato Amazon non è più globale! Ogni utente configura il proprio.

### 🛍️ Info prodotto via PA-API (opzionale)
Se vuoi che il bot mostri **titolo, prezzo e immagine** del prodotto nelle risposte:
1. Ottieni le chiavi PA-API da [Amazon Associates](https://affiliate-program.amazon.com/) (Amazon le concede dopo alcune vendite affiliate).
2. Installa la libreria opzionale: `pip install amazon-paapi`
3. Compila le variabili `PAAPI_*` nel file `.env`.

Se le chiavi/libreria mancano il bot funziona normalmente, convertendo i link in base all'ASIN.

### Ottenere il tuo ID Telegram (Per Admin)
1. Invia un messaggio a `@userinfobot`
2. Il bot ti risponderà con il tuo ID
3. Aggiungi l'ID nella variabile `ADMIN_IDS`

### Gestione Dati Utenti
I dati degli utenti sono salvati in `user_data.json` (automaticamente escluso da git).

**Struttura dati utente:**
```json
{
  "12345": {
    "affiliate_tag": "user-tag",
    "created_at": "2024-01-01T10:00:00", 
    "last_activity": "2024-01-01T12:30:00",
    "total_conversions": 42,
    "is_configured": true
  }
}
```

## 💡 Esempi di Utilizzo

### Configurazione Iniziale
```
👤 Utente: /start

🤖 Bot: Ciao! Per iniziare configura il tuo tag affiliato:
        /settag il-tuo-tag

👤 Utente: /settag mybrand-21

🤖 Bot: ✅ Configurazione completata!
        Il tuo tag: mybrand-21
        Ora puoi convertire link Amazon!
```

### Conversione Link
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