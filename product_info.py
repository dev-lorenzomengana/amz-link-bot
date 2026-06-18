"""
Arricchimento prodotto opzionale via Amazon Product Advertising API (PA-API 5).

Questo modulo è OPZIONALE e completamente "no-op" se le chiavi non sono configurate
o se la libreria PA-API non è installata: in quel caso il bot funziona esattamente
come prima, convertendo i link basandosi solo sull'ASIN.

Per attivarlo:
  1. Ottieni le chiavi PA-API da Amazon Associates (richiede qualche vendita affiliata
     prima che Amazon le conceda).
  2. Installa la libreria:  pip install amazon-paapi
  3. Compila in .env:  PAAPI_ACCESS_KEY, PAAPI_SECRET_KEY, PAAPI_PARTNER_TAG, PAAPI_COUNTRY
"""

import os
import logging
from functools import lru_cache
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Mappa dominio Amazon -> codice paese usato dalla libreria amazon-paapi
_DOMAIN_TO_COUNTRY = {
    'amazon.com': 'US',
    'amazon.it': 'IT',
    'amazon.co.uk': 'UK',
    'amazon.de': 'DE',
    'amazon.fr': 'FR',
    'amazon.es': 'ES',
    'amazon.ca': 'CA',
    'amazon.com.au': 'AU',
    'amazon.co.jp': 'JP',
    'amazon.in': 'IN',
    'amazon.com.br': 'BR',
    'amazon.com.mx': 'MX',
    'amazon.nl': 'NL',
    'amazon.se': 'SE',
    'amazon.pl': 'PL',
    'amazon.com.tr': 'TR',
    'amazon.ae': 'AE',
    'amazon.sa': 'SA',
    'amazon.sg': 'SG',
}


def is_configured() -> bool:
    """True se sono presenti tutte le chiavi PA-API nelle variabili d'ambiente."""
    return all(
        os.getenv(k)
        for k in ('PAAPI_ACCESS_KEY', 'PAAPI_SECRET_KEY', 'PAAPI_PARTNER_TAG')
    )


@lru_cache(maxsize=1)
def _get_api(country: str):
    """Crea (una sola volta) il client PA-API. Ritorna None se non disponibile."""
    if not is_configured():
        return None
    try:
        from amazon_paapi import AmazonApi  # import "lazy": dipendenza opzionale
    except ImportError:
        logger.info("Libreria 'amazon-paapi' non installata: arricchimento prodotto disattivato.")
        return None

    try:
        return AmazonApi(
            os.getenv('PAAPI_ACCESS_KEY'),
            os.getenv('PAAPI_SECRET_KEY'),
            os.getenv('PAAPI_PARTNER_TAG'),
            country,
        )
    except Exception as e:
        logger.warning(f"Impossibile inizializzare il client PA-API: {e}")
        return None


def get_product_info(asin: str, domain: str) -> Optional[Dict[str, str]]:
    """
    Ritorna {"title", "price", "image_url"} per un ASIN, oppure None se non disponibile.

    È sincrona e fa una chiamata di rete: nel bot va invocata con asyncio.to_thread.
    Qualsiasi errore o configurazione mancante => None (il bot prosegue normalmente).
    """
    if not is_configured():
        return None

    country = _DOMAIN_TO_COUNTRY.get(domain) or os.getenv('PAAPI_COUNTRY', 'US')
    api = _get_api(country)
    if api is None:
        return None

    try:
        items = api.get_items(asin)
        if not items:
            return None
        item = items[0]

        title = None
        if getattr(item, 'item_info', None) and getattr(item.item_info, 'title', None):
            title = item.item_info.title.display_value

        price = None
        listings = getattr(getattr(item, 'offers', None), 'listings', None)
        if listings:
            price_obj = getattr(listings[0], 'price', None)
            if price_obj:
                price = price_obj.display_amount

        image_url = None
        images = getattr(item, 'images', None)
        if images and getattr(images, 'primary', None) and getattr(images.primary, 'large', None):
            image_url = images.primary.large.url

        if not any((title, price, image_url)):
            return None

        return {"title": title, "price": price, "image_url": image_url}
    except Exception as e:
        logger.warning(f"PA-API: errore nel recupero del prodotto {asin}: {e}")
        return None
