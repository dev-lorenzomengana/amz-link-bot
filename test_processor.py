#!/usr/bin/env python3
"""
Test script per il bot Telegram Amazon Affiliate personalizzato
Testa sia il processore Amazon che il sistema di gestione utenti
"""

from amazon_processor import AmazonLinkProcessor
from user_manager import UserManager

def test_user_manager():
    """Test del sistema di gestione utenti."""
    print("🧪 Test User Manager")
    print("=" * 50)
    
    # Crea un user manager di test
    user_manager = UserManager("test_user_data.json")
    
    test_user_id = 12345
    test_tag = "test-tag-21"
    
    # Test configurazione utente
    print(f"🔧 Configurazione utente {test_user_id}")
    
    # Prima della configurazione
    is_configured_before = user_manager.is_user_configured(test_user_id)
    print(f"Configurato prima: {is_configured_before}")
    
    # Configura tag
    success = user_manager.set_affiliate_tag(test_user_id, test_tag)
    print(f"Configurazione riuscita: {success}")
    
    # Dopo la configurazione
    is_configured_after = user_manager.is_user_configured(test_user_id)
    tag_retrieved = user_manager.get_affiliate_tag(test_user_id)
    print(f"Configurato dopo: {is_configured_after}")
    print(f"Tag recuperato: {tag_retrieved}")
    
    # Test statistiche
    user_manager.increment_conversions(test_user_id, 3)
    stats = user_manager.get_user_stats(test_user_id)
    print(f"Statistiche utente: {stats}")
    
    # Test statistiche globali
    global_stats = user_manager.get_all_users_stats()
    print(f"Statistiche globali: {global_stats}")
    
    print("✅ Test User Manager completato\n")

def test_complete_workflow():
    """Test workflow completo: utente + conversione link."""
    print("🔄 Test Workflow Completo")
    print("=" * 50)
    
    # Inizializza componenti
    user_manager = UserManager("test_user_data.json")
    
    # Simula utenti
    users = [
        (11111, "user1-tag"),
        (22222, "user2-tag"), 
        (33333, "user3-tag")
    ]
    
    test_links = [
        "https://www.amazon.it/dp/B08N5WRWNW",
        "https://amazon.com/dp/B07ABC1234",
        "Guarda questo: https://www.amazon.de/dp/B09XYZ567 molto bello!"
    ]
    
    for user_id, user_tag in users:
        print(f"\n👤 Test per utente {user_id}")
        
        # Configura utente
        user_manager.set_affiliate_tag(user_id, user_tag)
        print(f"✓ Configurato con tag: {user_tag}")
        
        # Crea processore per questo utente
        processor = AmazonLinkProcessor(user_tag)
        
        for link in test_links:
            print(f"  🔗 Test link: {link[:50]}...")
            
            # Processa messaggio
            modified_message, affiliate_links = processor.process_message(link)
            
            if affiliate_links:
                print(f"  ✅ Convertiti: {len(affiliate_links)} link")
                print(f"     Primo link: {affiliate_links[0]}")
                
                # Aggiorna statistiche
                user_manager.increment_conversions(user_id, len(affiliate_links))
            else:
                print(f"  ❌ Nessun link Amazon trovato")
        
        # Mostra statistiche finali utente
        user_stats = user_manager.get_user_stats(user_id)
        print(f"  📊 Conversioni totali: {user_stats['total_conversions']}")
    
    # Statistiche finali globali
    print(f"\n📈 Statistiche Finali Globali:")
    global_stats = user_manager.get_all_users_stats()
    for key, value in global_stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Test Workflow Completo terminato")

def test_tag_validation():
    """Test validazione tag affiliato."""
    print("\n✅ Test Validazione Tag")
    print("=" * 30)
    
    user_manager = UserManager()
    
    test_cases = [
        # (tag, deve_essere_valido, descrizione)
        ("mytag-21", True, "Tag valido standard"),
        ("user123", True, "Tag solo alfanumerico"),
        ("my-awesome-tag", True, "Tag con trattini multipli"),
        ("user_tag", True, "Tag con underscore"),
        ("ab", False, "Troppo corto"),
        ("", False, "Tag vuoto"),
        ("tag-", False, "Finisce con trattino"),
        ("-tag", False, "Inizia con trattino"),
        ("tag with spaces", False, "Contiene spazi"),
        ("tag@invalid", False, "Caratteri non validi"),
        ("a" * 60, False, "Troppo lungo"),
    ]
    
    for tag, expected, description in test_cases:
        result = user_manager.validate_affiliate_tag(tag)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: '{tag}' -> {result}")

def test_amazon_processor():
    """Test del processore link: matching dominio, ASIN, no falsi positivi."""
    print("\n🔗 Test Amazon Processor")
    print("=" * 50)

    p = AmazonLinkProcessor("test-21")

    # (url, deve_essere_amazon, descrizione)
    domain_cases = [
        ("https://www.amazon.it/dp/B08N5WRWNW", True, "amazon.it standard"),
        ("https://amazon.com/dp/B07ABC1234", True, "amazon.com senza www"),
        ("https://amzn.to/3abcd", True, "short link amzn.to"),
        ("https://a.co/d/abcd", True, "short link a.co"),
        ("https://pizza.com/dp/B08N5WRWNW", False, "falso positivo a.co in pizza.com"),
        ("https://nonamazon.com.truffa.com/dp/B08N5WRWNW", False, "dominio camuffato"),
        ("https://google.com", False, "dominio non Amazon"),
    ]
    for url, expected, desc in domain_cases:
        result = p.is_amazon_link(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} {desc}: {url[:45]} -> {result}")

    # Estrazione ASIN
    asin_cases = [
        ("https://www.amazon.it/dp/B08N5WRWNW", "B08N5WRWNW"),
        ("https://www.amazon.it/gp/product/B07ABC1234", "B07ABC1234"),
        ("https://www.amazon.it/Some-Product-Name/dp/B09XYZ5678/ref=sr_1_1", "B09XYZ5678"),
        ("https://www.amazon.it/s?k=cuffie", None),
    ]
    print()
    for url, expected in asin_cases:
        result = p.extract_asin(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} ASIN '{url[:50]}' -> {result} (atteso {expected})")

    # Conversione (offline, resolve=False) — link lungo
    msg = "Guarda qui: https://www.amazon.de/dp/B08N5WRWNW grazie!"
    modified, links = p.process_message(msg, resolve=False)
    ok = links == ["https://www.amazon.de/dp/B08N5WRWNW?tag=test-21"]
    print(f"\n{'✅' if ok else '❌'} Conversione link lungo: {links}")


def test_expand_url_mock():
    """Test espansione short link senza rete (requests mockato)."""
    print("\n🌐 Test risoluzione short link (mock)")
    print("=" * 50)

    from unittest.mock import patch, MagicMock

    p = AmazonLinkProcessor("test-21")
    fake_resp = MagicMock()
    fake_resp.url = "https://www.amazon.it/dp/B08N5WRWNW?ref=xyz"

    with patch("amazon_processor.requests.head", return_value=fake_resp) as mock_head:
        modified, links = p.process_message("https://amzn.to/3abcd", resolve=True)
        expected = "https://www.amazon.it/dp/B08N5WRWNW?tag=test-21"
        ok = links == [expected]
        print(f"{'✅' if ok else '❌'} amzn.to risolto -> {links}")
        print(f"{'✅' if mock_head.called else '❌'} requests.head è stato chiamato")

    # Senza resolve, lo short link non produce conversione (nessun ASIN nell'URL)
    _, links_noresolve = p.process_message("https://amzn.to/3abcd", resolve=False)
    print(f"{'✅' if links_noresolve == [] else '❌'} Senza resolve: nessuna conversione (atteso)")


def interactive_user_test():
    """Test interattivo per simulare un utente."""
    print("\n💬 Test Interattivo Utente")
    print("=" * 30)
    
    user_manager = UserManager("test_user_data.json")
    
    print("Simula l'uso del bot da parte di un utente:")
    print("1. Configura il tuo tag affiliato")
    print("2. Testa la conversione link")
    print("3. Visualizza statistiche")
    print()
    
    # Configura utente
    test_user_id = 99999
    tag = input("Inserisci il tuo tag affiliato: ").strip()
    
    if not tag:
        print("❌ Test annullato")
        return
    
    if user_manager.set_affiliate_tag(test_user_id, tag):
        print(f"✅ Tag '{tag}' configurato con successo!")
    else:
        print(f"❌ Tag '{tag}' non valido!")
        return
    
    # Test conversioni
    processor = AmazonLinkProcessor(tag)
    
    print("\nOra puoi testare la conversione link (scrivi 'quit' per uscire):")
    
    while True:
        link = input("\nInserisci link Amazon: ").strip()
        
        if link.lower() in ['quit', 'exit', 'q']:
            break
        
        if not link:
            continue
        
        modified_message, affiliate_links = processor.process_message(link)
        
        if affiliate_links:
            print(f"✅ Convertito! Link con il tuo tag:")
            for aff_link in affiliate_links:
                print(f"   {aff_link}")
            
            user_manager.increment_conversions(test_user_id, len(affiliate_links))
        else:
            print("❌ Nessun link Amazon trovato")
    
    # Mostra statistiche finali
    stats = user_manager.get_user_stats(test_user_id)
    print(f"\n📊 Le tue statistiche finali:")
    print(f"   Tag: {stats['affiliate_tag']}")
    print(f"   Conversioni: {stats['total_conversions']}")

def cleanup_test_files():
    """Pulisce i file di test."""
    import os
    test_files = ["test_user_data.json"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Rimosso file di test: {file}")

if __name__ == "__main__":
    print("🧪 TEST BOT TELEGRAM AMAZON AFFILIATE PERSONALIZZATO")
    print("=" * 60)
    
    try:
        # Test componenti
        test_user_manager()
        test_tag_validation()
        test_amazon_processor()
        test_expand_url_mock()
        test_complete_workflow()
        
        # Test interattivo opzionale
        response = input("\nVuoi eseguire il test interattivo? (y/n): ")
        if response.lower() == 'y':
            interactive_user_test()
        
    except KeyboardInterrupt:
        print("\n\n❌ Test interrotti dall'utente")
    except Exception as e:
        print(f"\n❌ Errore durante i test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Pulizia
        cleanup_test_files()
        print("\n🎉 Test completati!")