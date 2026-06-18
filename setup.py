#!/usr/bin/env python3
"""
Script di setup per il bot Telegram Amazon Affiliate
Questo script ti guida nella configurazione iniziale del bot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica la versione di Python."""
    if sys.version_info < (3, 8):
        print("❌ Errore: Python 3.8 o superiore è richiesto")
        print(f"   Versione corrente: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
    return True

def install_dependencies():
    """Installa le dipendenze da requirements.txt."""
    print("\n📦 Installazione dipendenze...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dipendenze installate con successo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'installazione delle dipendenze:")
        print(f"   {e.stderr}")
        return False

def create_env_file():
    """Crea il file .env con configurazione guidata."""
    print("\n⚙️  Configurazione file .env")
    
    # Controlla se .env esiste già
    if os.path.exists('.env'):
        response = input("Il file .env esiste già. Vuoi sovrascriverlo? (y/n): ")
        if response.lower() != 'y':
            print("Configurazione .env saltata")
            return True
    
    print("\nPer configurare il bot, ho bisogno di alcune informazioni:")
    
    # Token del bot Telegram
    print("\n🤖 TOKEN BOT TELEGRAM")
    print("1. Vai su Telegram e cerca @BotFather")
    print("2. Invia /newbot e segui le istruzioni")
    print("3. Copia il token che ricevi")
    
    bot_token = input("\nInserisci il token del bot: ").strip()
    while not bot_token:
        bot_token = input("Token obbligatorio! Inserisci il token: ").strip()
    
    # ID Admin (opzionale)
    print("\n👑 ADMIN IDS (opzionale)")
    print("Per ottenere il tuo ID Telegram:")
    print("1. Invia un messaggio a @userinfobot")
    print("2. Il bot ti risponderà con il tuo ID")
    print("3. Gli admin possono vedere statistiche globali")
    
    admin_ids = input("\nInserisci gli ID admin (separati da virgole, o lascia vuoto): ").strip()
    
    # Informazioni sul nuovo sistema
    print("\n✨ IMPORTANTE - SISTEMA PERSONALIZZATO")
    print("• Ogni utente configurerà il proprio tag affiliato Amazon")
    print("• Non c'è più bisogno di un tag globale")
    print("• Gli utenti useranno /settag per configurare il loro tag")
    
    # Crea il file .env
    env_content = f"""# Configurazione Bot Telegram Amazon Affiliate Personalizzato

# Token del bot Telegram (obbligatorio)
TELEGRAM_BOT_TOKEN={bot_token}

# ID amministratori per statistiche globali (opzionale)
# Formato: ID1,ID2,ID3
ADMIN_IDS={admin_ids}

# NOTA: Il tag affiliato Amazon non è più globale!
# Ogni utente configura il proprio tag con /settag
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ File .env creato con successo")
        return True
    except Exception as e:
        print(f"❌ Errore nella creazione del file .env: {e}")
        return False

def test_configuration():
    """Testa la configurazione creata."""
    print("\n🧪 Test configurazione...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verifica le variabili d'ambiente
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_ids = os.getenv('ADMIN_IDS', '')
        
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN non trovato")
            return False
        
        print("✅ Token bot configurato")
        
        if admin_ids:
            print(f"✅ Admin IDs configurati: {admin_ids}")
        else:
            print("ℹ️  Nessun admin configurato (opzionale)")
        
        # Test del sistema di gestione utenti
        try:
            from user_manager import UserManager
            user_manager = UserManager("test_config.json")
            
            # Test configurazione utente di esempio
            test_user_id = 99999
            test_tag = "test-tag-21"
            
            success = user_manager.set_affiliate_tag(test_user_id, test_tag)
            if success:
                print("✅ Test sistema utenti: OK")
                
                # Test processore con tag utente
                from amazon_processor import AmazonLinkProcessor
                processor = AmazonLinkProcessor(test_tag)
                
                test_link = "https://www.amazon.it/dp/B08N5WRWNW"
                result = processor.create_affiliate_link(test_link)
                
                if result:
                    print(f"✅ Test processore Amazon: OK")
                    print(f"   Link di test: {result}")
                else:
                    print("❌ Test processore Amazon: FALLITO")
                    return False
                
                # Pulizia file di test
                import os
                if os.path.exists("test_config.json"):
                    os.remove("test_config.json")
                
            else:
                print("❌ Test configurazione utente: FALLITO")
                return False
                
        except Exception as e:
            print(f"❌ Errore nel test del sistema: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Errore nell'importazione: {e}")
        return False

def print_next_steps():
    """Stampa i prossimi passi da seguire."""
    print(f"""
🎉 SETUP COMPLETATO!

🚀 Prossimi passi:

1. 📱 AVVIA IL BOT:
   python main.py

2. 🔍 TESTA IL SISTEMA:
   python test_processor.py

3. 💬 USA IL BOT SU TELEGRAM:
   • Cerca il tuo bot su Telegram
   • Invia /start per iniziare
   • Ogni utente deve configurare il proprio tag con /settag

📋 CONFIGURAZIONE UTENTI:

🔧 Per ogni utente:
1. Invia /start al bot
2. Usa /settag il-tuo-tag-affiliato  
3. Esempio: /settag mybrand-21

🛒 Come ottenere il tag affiliato Amazon:
• Vai su https://affiliate-program.amazon.com/
• Accedi al tuo account Amazon Associates
• Trova il tuo tag nel dashboard
• Formato tipico: nome-tag-21

🎯 ESEMPIO COMPLETO:

Utente: /start
Bot: Configura il tuo tag con /settag

Utente: /settag mybrand-21  
Bot: ✅ Tag configurato!

Utente: https://amazon.it/dp/B08N5WRWNW
Bot: ✅ Link convertito con il tuo tag: 
     https://amazon.it/dp/B08N5WRWNW?tag=mybrand-21

📊 VANTAGGI SISTEMA PERSONALIZZATO:
• Ogni utente guadagna dalle proprie conversioni
• Nessuna condivisione di commissioni
• Statistiche personali per ogni utente
• Gestione dati GDPR compliant

🐛 TROUBLESHOOTING:
- Verifica che il token del bot sia corretto
- Controlla i log: tail -f bot.log
- Test: python test_processor.py

📚 DOCUMENTAZIONE COMPLETA:
   Leggi README.md per tutti i dettagli

Buon affiliate marketing personalizzato! 💰
""")

def main():
    """Funzione principale del setup."""
    print("=" * 60)
    print("🤖 SETUP BOT TELEGRAM AMAZON AFFILIATE PERSONALIZZATO")
    print("=" * 60)
    print("Ogni utente può configurare il proprio tag affiliato!")
    print()
    
    # Verifica Python
    if not check_python_version():
        return False
    
    # Installa dipendenze
    if not install_dependencies():
        print("\n❌ Setup interrotto: errore nell'installazione delle dipendenze")
        return False
    
    # Crea file .env
    if not create_env_file():
        print("\n❌ Setup interrotto: errore nella configurazione")
        return False
    
    # Testa configurazione
    if not test_configuration():
        print("\n⚠️  Setup completato ma ci sono problemi nella configurazione")
        print("   Controlla il file .env e riprova")
        return False
    
    # Istruzioni finali
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        sys.exit(1)