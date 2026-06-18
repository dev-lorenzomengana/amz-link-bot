#!/usr/bin/env python3
"""
Bot Telegram per convertire link Amazon in link affiliati
"""

import os
import io
import json
import uuid
import asyncio
import logging
from typing import List
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    InlineQueryResultArticle,
    InlineQueryResultsButton,
    InputTextMessageContent,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from amazon_processor import AmazonLinkProcessor
from user_manager import UserManager
import product_info

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramAmazonBot:
    """Bot Telegram per convertire link Amazon in link affiliati."""

    # Comandi mostrati nel menu "/" di Telegram e nel messaggio di aiuto.
    # (comando, emoji, descrizione) — unica fonte di verità per menu + fallback.
    MENU_COMMANDS = [
        ("start", "🚀", "Inizia e configura il bot"),
        ("settag", "🏷️", "Configura il tuo tag affiliato Amazon"),
        ("settings", "⚙️", "Gestisci le tue impostazioni"),
        ("mystats", "📊", "Le tue statistiche personali"),
        ("export", "📦", "Esporta i tuoi dati (GDPR)"),
        ("deletedata", "🗑️", "Elimina i tuoi dati (GDPR)"),
        ("help", "❓", "Guida completa all'uso"),
    ]

    def __init__(self):
        # Configurazione dalle variabili d'ambiente
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_ids = self._parse_admin_ids()
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN non trovato nelle variabili d'ambiente")
        
        # Inizializza il gestore utenti
        self.user_manager = UserManager()
        
        # Statistiche globali
        self.stats = {
            'messages_processed': 0,
            'links_converted': 0,
            'users': set()
        }
    
    def _parse_admin_ids(self) -> List[int]:
        """Parsa gli ID admin dalle variabili d'ambiente."""
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if not admin_ids_str:
            return []
        
        try:
            return [int(id_str.strip()) for id_str in admin_ids_str.split(',') if id_str.strip()]
        except ValueError:
            logger.warning("Errore nel parsing degli ADMIN_IDS")
            return []

    @staticmethod
    def _escape_md(text: str) -> str:
        """Esegue l'escape dei caratteri speciali del Markdown legacy di Telegram."""
        if not text:
            return ""
        for ch in ('_', '*', '`', '['):
            text = text.replace(ch, '\\' + ch)
        return text
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /start."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Utente"
        
        # Controlla se l'utente è già configurato
        if self.user_manager.is_user_configured(user_id):
            user_stats = self.user_manager.get_user_stats(user_id)
            welcome_message = f"""
🎉 **Bentornato, {user_name}!**

Il tuo bot Amazon Affiliate è già configurato e pronto all'uso!

📊 **Le tue statistiche:**
• Tag affiliato: `{user_stats['affiliate_tag']}`
• Link convertiti: {user_stats['total_conversions']}

**Come usarlo:**
• Invia un messaggio con un link Amazon
• Riceverai automaticamente il link con il tuo tag affiliato

**Comandi disponibili:**
Usa il **menu comandi** (icona "/" nel tastierino) per accedere rapidamente a:
• `/settings` - Gestisci le tue impostazioni
• `/mystats` - Le tue statistiche personali  
• `/help` - Guida dettagliata

Inizia subito inviandomi un link Amazon! 🛒
            """
        else:
            welcome_message = f"""
👋 **Ciao {user_name}! Benvenuto nel Bot Amazon Affiliate**

🎯 **Configurazione Richiesta**
Per utilizzare il bot, devi prima configurare il tuo tag affiliato Amazon.

**Come configurare:**
1. Usa il comando `/settag tuo-tag-affiliato`
2. Esempio: `/settag mytag-21`

**Come ottenere il tag affiliato:**
• Accedi ad [Amazon Associates](https://affiliate-program.amazon.com/)
• Trova il tuo tag nel dashboard
• Di solito ha formato: `nome-tag-21`

**Una volta configurato potrai:**
• Convertire automaticamente i link Amazon
• Guadagnare commissioni sui tuoi link
• Tracciare le tue statistiche

**Comandi disponibili:**
Usa il **menu comandi** (icona "/" nel tastierino) per accesso rapido:
• `/settag` - Configura il tuo tag affiliato
• `/help` - Guida completa
• `/settings` - Impostazioni

Inizia con `/settag il-tuo-tag` per configurare il bot! 🚀
            """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /help."""
        help_message = """
📚 **Guida Completa del Bot**

🤖 **Cosa fa questo bot:**
Converte automaticamente i link Amazon usando il TUO tag affiliato personale!

🚀 **Setup iniziale:**
1. Usa `/start` per iniziare
2. Configura il tuo tag: `/settag il-tuo-tag-affiliato`
3. Esempio: `/settag mystore-21`

💬 **Come usare:**
• Invia qualsiasi messaggio con un link Amazon
• Il bot risponderà con il link convertito usando il tuo tag
• Guadagni commissioni su ogni acquisto tramite i tuoi link!

📱 **Comandi disponibili:**
Usa il **menu comandi** (icona "/" o "☰") per vedere tutti i comandi:

• `/start` - Configurazione iniziale
• `/settag <tag>` - Configura/cambia tag affiliato  
• `/settings` - Gestisci impostazioni account
• `/mystats` - Le tue statistiche personali
• `/export` - Esporta i tuoi dati (GDPR)
• `/deletedata` - Elimina i tuoi dati
• `/help` - Questa guida

💡 **Modalità inline:** scrivi `@nomebot link-amazon` in QUALSIASI chat per inviare al volo il link affiliato!

🌍 **Domini supportati:**
amazon.it, amazon.com, amazon.de, amazon.co.uk, amazon.fr, amazon.es, amazon.ca, amazon.com.au, amzn.to e molti altri!

🛒 **Come ottenere il tag affiliato:**
1. Vai su [Amazon Associates](https://affiliate-program.amazon.com/)
2. Accedi al tuo account
3. Trova il tuo tag nel dashboard
4. Formato tipico: `nome-tag-21`

💰 **Ogni utente guadagna le proprie commissioni - nessuna condivisione!**
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def settag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /settag per configurare il tag affiliato."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Utente"
        
        # Verifica se è stato fornito un tag
        if not context.args:
            current_tag = self.user_manager.get_affiliate_tag(user_id)
            if current_tag:
                help_message = f"""
⚙️ **Configurazione Tag Affiliato**

Il tuo tag attuale: `{current_tag}`

**Per cambiarlo:**
`/settag nuovo-tag-affiliato`

**Esempio:**
`/settag mionuovotag-21`

**Formato valido:**
• Solo lettere, numeri, trattini e underscore
• Lunghezza: 3-50 caratteri
• Non può iniziare/finire con trattino
                """
            else:
                help_message = """
⚙️ **Configura il tuo Tag Affiliato**

**Uso:** `/settag tuo-tag-affiliato`

**Esempio:** `/settag mytag-21`

**Come ottenere il tag:**
1. Vai su [Amazon Associates](https://affiliate-program.amazon.com/)
2. Accedi al tuo account
3. Trova il tuo tag nel dashboard
4. Copialo e usalo qui

**Formato richiesto:**
• Solo lettere, numeri, trattini
• Lunghezza: 3-50 caratteri
• Esempio: `nomeutente-21`
                """
            
            await update.message.reply_text(help_message, parse_mode='Markdown', disable_web_page_preview=True)
            return
        
        # Ottieni il tag dall'argomento
        new_tag = context.args[0].strip()
        
        # Valida il tag
        if not self.user_manager.validate_affiliate_tag(new_tag):
            error_message = """
❌ **Tag non valido!**

**Requisiti del tag:**
• 3-50 caratteri
• Solo lettere, numeri, trattini, underscore
• Non può iniziare/finire con trattino

**Esempi validi:**
• `mytag-21`
• `username-affiliato`
• `store_name123`

**Esempi NON validi:**
• `-badtag` (inizia con trattino)
• `badtag-` (finisce con trattino)
• `bad tag` (contiene spazi)
• `ab` (troppo corto)

Riprova con un tag valido!
            """
            await update.message.reply_text(error_message, parse_mode='Markdown')
            return
        
        # Imposta il tag
        old_tag = self.user_manager.get_affiliate_tag(user_id)
        if self.user_manager.set_affiliate_tag(user_id, new_tag):
            if old_tag:
                success_message = f"""
✅ **Tag affiliato aggiornato con successo!**

**Vecchio tag:** `{old_tag}`
**Nuovo tag:** `{new_tag}`

🎉 Ora puoi inviare link Amazon e verranno convertiti automaticamente con il tuo nuovo tag!

**Prova subito:**
Invia un link Amazon per testare la conversione.
                """
            else:
                success_message = f"""
🎉 **Configurazione completata!**

**Il tuo tag affiliato:** `{new_tag}`

Ora sei pronto a convertire link Amazon! 

**Come usare:**
1. Invia un messaggio con un link Amazon
2. Riceverai automaticamente il link convertito
3. Guadagna commissioni sui click!

**Prova subito:**
Invia un link Amazon per vedere la magia! ✨
                """
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            
            # Log per admin
            logger.info(f"Utente {user_id} ({user_name}) ha configurato il tag: {new_tag}")
        else:
            await update.message.reply_text("❌ Errore nella configurazione del tag. Riprova.")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /settings."""
        user_id = update.effective_user.id
        user_stats = self.user_manager.get_user_stats(user_id)
        
        if not self.user_manager.is_user_configured(user_id):
            settings_message = """
⚙️ **Impostazioni**

❌ **Account non configurato**

Usa `/settag tuo-tag-affiliato` per iniziare!
            """
        else:
            from datetime import datetime
            try:
                created_date = datetime.fromisoformat(user_stats['created_at']).strftime("%d/%m/%Y")
            except:
                created_date = "Sconosciuta"
            
            settings_message = f"""
⚙️ **Le tue Impostazioni**

👤 **Account:**
• Stato: ✅ Configurato
• Tag affiliato: `{user_stats['affiliate_tag']}`
• Membro dal: {created_date}

📊 **Statistiche:**
• Link convertiti: {user_stats['total_conversions']}

🔧 **Azioni disponibili:**
• `/settag nuovo-tag` - Cambia tag affiliato
• `/mystats` - Statistiche dettagliate
• `/deletedata` - Elimina tutti i dati

**Nota:** Le commissioni vengono generate quando qualcuno clicca sui tuoi link convertiti e acquista su Amazon.
            """
        
        await update.message.reply_text(settings_message, parse_mode='Markdown')
    
    async def mystats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /mystats."""
        user_id = update.effective_user.id
        
        if not self.user_manager.is_user_configured(user_id):
            await update.message.reply_text(
                "❌ **Account non configurato**\n\nUsa `/settag tuo-tag-affiliato` per iniziare!",
                parse_mode='Markdown'
            )
            return
        
        user_stats = self.user_manager.get_user_stats(user_id)
        
        try:
            from datetime import datetime
            created_date = datetime.fromisoformat(user_stats['created_at']).strftime("%d/%m/%Y alle %H:%M")
            last_activity = datetime.fromisoformat(user_stats['last_activity']).strftime("%d/%m/%Y alle %H:%M")
        except:
            created_date = "Sconosciuta"
            last_activity = "Sconosciuta"
        
        stats_message = f"""
📊 **Le tue Statistiche Personali**

👤 **Informazioni Account:**
• Tag affiliato: `{user_stats['affiliate_tag']}`
• Account creato: {created_date}
• Ultima attività: {last_activity}

📈 **Attività:**
• Link Amazon convertiti: **{user_stats['total_conversions']}**

💡 **Suggerimenti:**
• Condividi i tuoi link convertiti sui social
• Più click = più possibilità di commissioni
• Ogni acquisto tramite i tuoi link ti fa guadagnare!

🎯 **Prossimi obiettivi:**
• Raggiungi 10 conversioni per sbloccare statistiche avanzate
• Condividi il bot con gli amici!
        """
        
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    
    async def deletedata_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per eliminare i dati utente (GDPR compliance)."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Utente"
        
        # Messaggio di conferma
        confirm_message = f"""
⚠️ **Eliminazione Dati Account**

{user_name}, sei sicuro di voler eliminare tutti i tuoi dati?

**Cosa verrà eliminato:**
• Il tuo tag affiliato
• Tutte le tue statistiche
• Le impostazioni dell'account

**Nota:** Questa azione è irreversibile!

**Per confermare, invia:** `/confermaeliminazione`
**Per annullare, invia:** `/annulla`
        """
        
        await update.message.reply_text(confirm_message, parse_mode='Markdown')
    
    async def confirm_delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Conferma l'eliminazione dei dati utente."""
        user_id = update.effective_user.id
        
        if self.user_manager.delete_user_data(user_id):
            success_message = """
✅ **Dati eliminati con successo**

Tutti i tuoi dati sono stati rimossi dal sistema.

Per utilizzare nuovamente il bot, dovrai configurare il tuo tag affiliato con `/settag`.

Grazie per aver utilizzato il nostro servizio!
            """
        else:
            success_message = """
ℹ️ **Nessun dato da eliminare**

Non abbiamo trovato dati associati al tuo account.
            """
        
        await update.message.reply_text(success_message, parse_mode='Markdown')
        
        # Log per admin
        logger.info(f"Utente {user_id} ha eliminato i suoi dati")
    
    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per /export: invia all'utente tutti i suoi dati in JSON (GDPR)."""
        user_id = update.effective_user.id

        if not self.user_manager.is_user_configured(user_id):
            await update.message.reply_text(
                "ℹ️ Non ci sono dati da esportare. Usa `/settag` per iniziare!",
                parse_mode='Markdown'
            )
            return

        data = self.user_manager.export_user_data(user_id)
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        buffer = io.BytesIO(payload)
        buffer.name = f"miei_dati_{user_id}.json"

        await update.message.reply_document(
            document=buffer,
            filename=buffer.name,
            caption="📦 Ecco l'esportazione completa dei tuoi dati (GDPR)."
        )
        logger.info(f"Utente {user_id} ha esportato i propri dati")

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Modalità inline: @nomebot <link Amazon> in qualsiasi chat."""
        query = update.inline_query
        user_id = query.from_user.id
        text = (query.query or "").strip()

        # Utente non configurato: invitalo ad aprire il bot per impostare il tag
        if not self.user_manager.is_user_configured(user_id):
            await query.answer(
                results=[],
                button=InlineQueryResultsButton(
                    text="⚙️ Configura il tuo tag affiliato",
                    start_parameter="setup",
                ),
                cache_time=5,
                is_personal=True,
            )
            return

        if not text:
            await query.answer(results=[], cache_time=5, is_personal=True)
            return

        user_tag = self.user_manager.get_affiliate_tag(user_id)
        processor = AmazonLinkProcessor(user_tag)
        conversions = await asyncio.to_thread(processor.build_results, text, True)

        results = []
        for r in conversions:
            affiliate = r["affiliate"]
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="🔗 Link affiliato pronto",
                    description=affiliate,
                    input_message_content=InputTextMessageContent(
                        message_text=affiliate,
                        disable_web_page_preview=False,
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🛒 Apri su Amazon", url=affiliate)]
                    ]),
                )
            )

        if conversions:
            self.user_manager.increment_conversions(user_id, len(conversions))

        await query.answer(results=results, cache_time=5, is_personal=True)

    def _build_commands_text(self) -> str:
        """Costruisce l'elenco comandi (con spiegazione) dalla lista condivisa."""
        lines = []
        for name, emoji, desc in self.MENU_COMMANDS:
            arg = " <tag>" if name == "settag" else ""
            lines.append(f"{emoji} `/{name}{arg}` — {desc}")
        return "\n".join(lines)

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Risponde ai comandi /sconosciuti spiegando quelli disponibili."""
        attempted = ""
        if update.message and update.message.text:
            attempted = update.message.text.split()[0]

        message = f"""🤔 **Comando non riconosciuto**

Non conosco il comando `{attempted}`. Ecco cosa puoi fare:

{self._build_commands_text()}

💡 Tocca l'icona **"/"** nel tastierino per vedere i comandi con la spiegazione, oppure inviami direttamente un **link Amazon** e lo converto con il tuo tag!"""

        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True,
        )

    async def setup_bot_commands(self, application: Application):
        """Configura i comandi visibili nel menu di Telegram."""
        commands = [
            BotCommand(name, f"{emoji} {desc}")
            for name, emoji, desc in self.MENU_COMMANDS
        ]

        # Imposta i comandi per tutti gli utenti (compaiono digitando "/")
        await application.bot.set_my_commands(commands)
        
        # Imposta la descrizione del bot
        bot_description = """🤖 Bot Amazon Affiliate Personalizzato

Converte automaticamente i link Amazon usando il TUO tag affiliato personale!

🚀 Per iniziare: /start
🏷️ Configura tag: /settag tuo-tag"""
        
        try:
            await application.bot.set_my_description(bot_description)
            logger.info("Descrizione bot configurata")
        except Exception as e:
            logger.warning(f"Impossibile configurare descrizione bot: {e}")
        
        # Imposta la descrizione breve del bot
        try:
            await application.bot.set_my_short_description("Converte link Amazon con il tuo tag affiliato personale!")
            logger.info("Descrizione breve bot configurata")
        except Exception as e:
            logger.warning(f"Impossibile configurare descrizione breve: {e}")
        
        logger.info("Menu comandi configurato in Telegram - comandi visibili nel tastierino")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /stats (solo admin)."""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("❌ Comando disponibile solo per gli amministratori.")
            return
        
        # Ottieni statistiche globali
        global_stats = self.user_manager.get_all_users_stats()
        recent_users = self.user_manager.get_recent_users(7)
        
        stats_message = f"""
📊 **Statistiche Bot Admin**

👥 **Utenti:**
• Totale utenti: {global_stats['total_users']}
• Utenti configurati: {global_stats['configured_users']}
• Utenti non configurati: {global_stats['unconfigured_users']}
• Attivi ultimi 7 giorni: {recent_users}

📈 **Conversioni:**
• Link convertiti totali: {global_stats['total_conversions']}
• Media per utente: {global_stats['average_conversions']:.1f}

🔧 **Sistema:**
• Messaggi processati (sessione): {self.stats['messages_processed']}
• Link convertiti (sessione): {self.stats['links_converted']}
• Utenti attivi (sessione): {len(self.stats['users'])}

📱 **Configurazione:**
• Admin configurati: {len(self.admin_ids)}
• Bot operativo: ✅
        """
        
        await update.message.reply_text(
            stats_message,
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principale per i messaggi con link Amazon."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Utente"
        message_text = update.message.text
        
        # Aggiorna statistiche globali
        self.stats['messages_processed'] += 1
        self.stats['users'].add(user_id)
        
        # Verifica se l'utente è configurato
        if not self.user_manager.is_user_configured(user_id):
            not_configured_message = f"""
⚙️ **Configurazione Richiesta**

Ciao {user_name}! Per convertire i link Amazon devi prima configurare il tuo tag affiliato.

**Per iniziare:**
`/settag il-tuo-tag-affiliato`

**Esempio:**
`/settag mytag-21`

**Come ottenere il tag:**
• Accedi ad [Amazon Associates](https://affiliate-program.amazon.com/)
• Trova il tuo tag nel dashboard

Una volta configurato, potrai convertire automaticamente tutti i link Amazon! 🚀
            """
            
            await update.message.reply_text(
                not_configured_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return
        
        # Ottieni il tag affiliato dell'utente
        user_tag = self.user_manager.get_affiliate_tag(user_id)
        
        if not user_tag:
            await update.message.reply_text(
                "❌ Errore nel recupero del tuo tag affiliato. Usa `/settag` per riconfigurarlo.",
                parse_mode='Markdown'
            )
            return
        
        # Crea un processore Amazon per questo utente
        user_processor = AmazonLinkProcessor(user_tag)

        # Processa il messaggio per trovare link Amazon.
        # resolve=True segue i redirect degli short link (amzn.to, a.co, ...):
        # è una chiamata di rete bloccante, quindi la eseguiamo in un thread per
        # non bloccare l'event loop asincrono.
        results = await asyncio.to_thread(user_processor.build_results, message_text, True)
        modified_message = message_text
        for r in results:
            modified_message = modified_message.replace(r["original"], r["affiliate"])
        affiliate_links = [r["affiliate"] for r in results]

        if not affiliate_links:
            # Nessun link Amazon trovato
            no_links_message = """
🔍 **Nessun link Amazon trovato**

Inviami un messaggio con un link Amazon e lo convertirò automaticamente con il tuo tag affiliato!

**Domini supportati:**
• amazon.it, amazon.com, amazon.de
• amazon.co.uk, amazon.fr, amazon.es
• amzn.to (link corti)
• E molti altri...

**Esempio:**
`https://www.amazon.it/dp/B08N5WRWNW`
            """
            
            await update.message.reply_text(no_links_message, parse_mode='Markdown')
            return
        
        # Aggiorna statistiche
        self.stats['links_converted'] += len(affiliate_links)
        self.user_manager.increment_conversions(user_id, len(affiliate_links))

        # Conteggio per i testi
        if len(affiliate_links) == 1:
            emoji = "🔗"
            count_text = "Link Amazon convertito"
        else:
            emoji = "🔗✨"
            count_text = f"{len(affiliate_links)} link Amazon convertiti"

        # Arricchimento prodotto opzionale (PA-API): solo per un singolo link e se configurato
        product = None
        if len(results) == 1 and product_info.is_configured():
            try:
                product = await asyncio.to_thread(
                    product_info.get_product_info,
                    results[0]["asin"],
                    results[0]["domain"],
                )
            except Exception as e:
                logger.warning(f"Arricchimento prodotto fallito: {e}")

        # I link affiliati sono mostrati in blocco `code` (copiabili e a prova di Markdown)
        links_block = "\n".join(f"`{link}`" for link in affiliate_links)

        product_block = ""
        if product:
            if product.get("title"):
                product_block += f"\n📦 *{self._escape_md(product['title'])}*"
            if product.get("price"):
                product_block += f"\n💶 Prezzo: *{self._escape_md(product['price'])}*"

        response_message = f"""✅ **{count_text} con il tuo tag!**
{product_block}

{links_block}

🏷️ Tag utilizzato: `{user_tag}`
💰 _Ora guadagni commissioni su ogni acquisto tramite questi link!_"""

        # Keyboard: un bottone "Apri su Amazon" per ogni link (max 3) + statistiche
        keyboard = []
        for link in affiliate_links[:3]:
            keyboard.append([InlineKeyboardButton("🛒 Apri su Amazon", url=link)])
        keyboard.append([
            InlineKeyboardButton("📊 Statistiche", callback_data="user_stats"),
            InlineKeyboardButton("⚙️ Impostazioni", callback_data="settings"),
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Se abbiamo un'immagine prodotto, inviala con didascalia
        try:
            if product and product.get("image_url"):
                await update.message.reply_photo(
                    photo=product["image_url"],
                    caption=response_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                )
            else:
                await update.message.reply_text(
                    response_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
        except Exception as e:
            # Fallback senza markdown se ci sono errori di formato
            logger.warning(f"Invio risposta in Markdown fallito ({e}), uso testo semplice")
            simple_links = "\n".join(affiliate_links)
            simple_response = f"✅ {count_text} con il tuo tag: {user_tag}\n\n{simple_links}"
            await update.message.reply_text(simple_response, reply_markup=reply_markup)

        # Log per monitoraggio
        logger.info(f"Utente {user_id} ({user_name}): convertiti {len(affiliate_links)} link con tag {user_tag}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per i callback delle keyboard inline."""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        if query.data == "info":
            info_message = """
🤖 **Amazon Affiliate Bot Personalizzato**

Questo bot converte i link Amazon usando il TUO tag affiliato personale!

**Caratteristiche:**
• Ogni utente ha il proprio tag affiliato
• Mantiene la localizzazione originale (amazon.it, amazon.com, etc.)
• Formato pulito e professionale
• Statistiche personali

**Privacy:**
• I tuoi dati rimangono privati
• Compliance GDPR (puoi eliminare i dati)
• Non condividiamo i tuoi tag affiliati

Sviluppato per massimizzare le TUE commissioni! 💰
            """
            await query.message.reply_text(info_message, parse_mode='Markdown')
            
        elif query.data == "user_stats":
            if not self.user_manager.is_user_configured(user_id):
                await query.message.reply_text(
                    "❌ Account non configurato. Usa `/settag` per iniziare!",
                    parse_mode='Markdown'
                )
                return
            
            user_stats = self.user_manager.get_user_stats(user_id)
            
            stats_message = f"""
📊 **Le tue Statistiche**

👤 **Account:** `{user_stats['affiliate_tag']}`
📈 **Link convertiti:** {user_stats['total_conversions']}

💡 **Suggerimento:** 
Condividi i tuoi link convertiti per guadagnare commissioni!

Usa `/mystats` per statistiche dettagliate.
            """
            await query.message.reply_text(stats_message, parse_mode='Markdown')
            
        elif query.data == "settings":
            if not self.user_manager.is_user_configured(user_id):
                await query.message.reply_text(
                    "❌ Account non configurato. Usa `/settag` per iniziare!",
                    parse_mode='Markdown'
                )
                return
            
            user_tag = self.user_manager.get_affiliate_tag(user_id)
            settings_message = f"""
⚙️ **Impostazioni Rapide**

🏷️ **Tag attuale:** `{user_tag}`

**Comandi disponibili:**
• `/settag nuovo-tag` - Cambia tag
• `/mystats` - Statistiche complete
• `/settings` - Impostazioni dettagliate

Tutto configurato! 👍
            """
            await query.message.reply_text(settings_message, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per gli errori."""
        logger.error(f"Errore: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Si è verificato un errore. Riprova tra poco."
            )
    
    def run(self):
        """Avvia il bot."""
        # Crea l'applicazione
        application = Application.builder().token(self.token).build()
        
        # Aggiungi gli handler
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Handler per configurazione utente
        application.add_handler(CommandHandler("settag", self.settag_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CommandHandler("mystats", self.mystats_command))
        application.add_handler(CommandHandler("export", self.export_command))
        application.add_handler(CommandHandler("deletedata", self.deletedata_command))
        application.add_handler(CommandHandler("confermaeliminazione", self.confirm_delete_command))

        # Alias per comandi comuni
        application.add_handler(CommandHandler("config", self.settings_command))
        application.add_handler(CommandHandler("setup", self.settag_command))
        application.add_handler(CommandHandler("annulla", self.start_command))  # Reindirizza al start

        # Handler per messaggi con testo (possibili link)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Comandi sconosciuti: aggiunto DOPO i CommandHandler, scatta solo se nessuno
        # ha gestito il comando -> mostra l'elenco con le spiegazioni
        application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))

        # Handler per la modalità inline (@nomebot <link> in qualsiasi chat)
        application.add_handler(InlineQueryHandler(self.inline_query))

        # Handler per callback
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Handler per errori
        application.add_error_handler(self.error_handler)
        
        # Aggiungi hook per configurare i comandi all'avvio
        application.post_init = self.setup_bot_commands
        
        # Avvia il bot
        logger.info("Avvio del bot Amazon Affiliate Link Converter (Personalizzato)...")
        logger.info("Bot configurato per tag affiliati personalizzati per utente")
        
        # Statistiche iniziali
        stats = self.user_manager.get_all_users_stats()
        logger.info(f"Utenti totali nel sistema: {stats['total_users']}")
        logger.info(f"Utenti configurati: {stats['configured_users']}")
        
        # Avvia il polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

def main():
    """Funzione principale."""
    try:
        bot = TelegramAmazonBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot fermato dall'utente")
    except Exception as e:
        logger.error(f"Errore critico: {e}")
        raise

if __name__ == "__main__":
    main()