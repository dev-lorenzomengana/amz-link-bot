import re
import logging
import urllib.parse
from typing import List, Optional, Tuple, Dict

import requests

logger = logging.getLogger(__name__)

# User-Agent "da browser": alcuni shortener Amazon rispondono male a client generici
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class AmazonLinkProcessor:
    """Classe per gestire i link Amazon e convertirli in link affiliati."""

    # Domini Amazon "veri" (storefront) su cui costruiamo il link affiliato
    AMAZON_DOMAINS = [
        'amazon.com', 'amazon.it', 'amazon.co.uk', 'amazon.de',
        'amazon.fr', 'amazon.es', 'amazon.ca', 'amazon.com.au',
        'amazon.co.jp', 'amazon.in', 'amazon.com.br', 'amazon.com.mx',
        'amazon.nl', 'amazon.se', 'amazon.pl', 'amazon.com.tr',
        'amazon.ae', 'amazon.sa', 'amazon.sg',
    ]

    # Shortener/redirect: NON contengono l'ASIN, vanno risolti seguendo il redirect
    SHORT_LINK_DOMAINS = ['amzn.to', 'amzn.eu', 'a.co', 'amzn.asia']

    # Mappa shortener -> dominio di fallback se non riusciamo a risolverli
    _SHORT_DOMAIN_FALLBACK = {
        'amzn.to': 'amazon.com',
        'amzn.eu': 'amazon.de',
        'amzn.asia': 'amazon.co.jp',
        'a.co': 'amazon.com',
    }

    def __init__(self, affiliate_tag: str):
        self.affiliate_tag = affiliate_tag

        # Pattern regex per estrarre ASIN dai link Amazon.
        # I pattern espliciti vengono provati per primi; quello generico è l'ultima risorsa.
        self.asin_patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/gp/aw/d/([A-Z0-9]{10})',
            r'/product-reviews/([A-Z0-9]{10})',
            r'/ASIN/([A-Z0-9]{10})',
            r'[?&]asin=([A-Z0-9]{10})',
            # Generico: un segmento di path di 10 caratteri (non nella query string)
            r'/([A-Z0-9]{10})(?:[/?#]|$)',
        ]

    # ------------------------------------------------------------------ #
    # Helpers dominio
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_netloc(url: str) -> str:
        """Estrae il dominio (senza www.) da un URL."""
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        # Rimuovi eventuale porta
        if ':' in domain:
            domain = domain.split(':', 1)[0]
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    @staticmethod
    def _domain_matches(netloc: str, base: str) -> bool:
        """True se netloc è esattamente base o un suo sottodominio (no match per sottostringa)."""
        return netloc == base or netloc.endswith('.' + base)

    def is_amazon_link(self, url: str) -> bool:
        """Verifica se il link è di Amazon (storefront o shortener)."""
        try:
            domain = self._normalize_netloc(url)
            all_domains = self.AMAZON_DOMAINS + self.SHORT_LINK_DOMAINS
            return any(self._domain_matches(domain, base) for base in all_domains)
        except Exception:
            return False

    def is_short_link(self, url: str) -> bool:
        """True se l'URL è uno shortener Amazon (da risolvere via redirect)."""
        try:
            domain = self._normalize_netloc(url)
            return any(self._domain_matches(domain, base) for base in self.SHORT_LINK_DOMAINS)
        except Exception:
            return False

    def get_amazon_domain_from_url(self, url: str) -> str:
        """Estrae il dominio Amazon dall'URL per mantenere la localizzazione."""
        try:
            domain = self._normalize_netloc(url)
            # Match esatto su uno dei domini storefront
            for base in self.AMAZON_DOMAINS:
                if self._domain_matches(domain, base):
                    return base
            # Shortener non risolto: usa il fallback
            for short, fallback in self._SHORT_DOMAIN_FALLBACK.items():
                if self._domain_matches(domain, short):
                    return fallback
            return 'amazon.com'
        except Exception:
            return 'amazon.com'

    # ------------------------------------------------------------------ #
    # Estrazione link / ASIN
    # ------------------------------------------------------------------ #
    def extract_links_from_message(self, message_text: str) -> List[str]:
        """Estrae tutti i link http(s) dal messaggio, ripulendo la punteggiatura finale."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message_text)
        # Rimuovi punteggiatura/parentesi che spesso seguono un URL in una frase
        cleaned = [u.rstrip('.,);:!?»"\'') for u in urls]
        return cleaned

    def expand_url(self, url: str) -> str:
        """Risolve uno shortener seguendo i redirect. Ritorna l'URL originale in caso di errore."""
        try:
            resp = requests.head(
                url,
                allow_redirects=True,
                timeout=6,
                headers={'User-Agent': _BROWSER_UA},
            )
            final_url = resp.url
            # Alcuni server non gestiscono HEAD: riprova con GET se non c'è stato redirect utile
            if not final_url or self.is_short_link(final_url):
                resp = requests.get(
                    url,
                    allow_redirects=True,
                    timeout=6,
                    stream=True,
                    headers={'User-Agent': _BROWSER_UA},
                )
                final_url = resp.url
                resp.close()
            return final_url or url
        except requests.RequestException as e:
            logger.warning(f"Impossibile risolvere lo short link {url}: {e}")
            return url

    def extract_asin(self, url: str) -> Optional[str]:
        """Estrae l'ASIN dal link Amazon."""
        for pattern in self.asin_patterns:
            match = re.search(pattern, url)
            if match:
                asin = match.group(1)
                if len(asin) == 10 and re.match(r'^[A-Z0-9]{10}$', asin):
                    return asin
        return None

    def create_affiliate_link(self, original_url: str) -> Optional[str]:
        """Converte un link Amazon (già risolto) in link affiliato pulito."""
        if not self.is_amazon_link(original_url):
            return None

        asin = self.extract_asin(original_url)
        if not asin:
            return None

        domain = self.get_amazon_domain_from_url(original_url)
        return f"https://www.{domain}/dp/{asin}?tag={self.affiliate_tag}"

    # ------------------------------------------------------------------ #
    # Processo messaggio
    # ------------------------------------------------------------------ #
    def build_results(self, message_text: str, resolve: bool = False) -> List[Dict[str, str]]:
        """
        Restituisce una lista strutturata di risultati per ogni link Amazon convertito.

        Ogni elemento: {"original", "resolved", "asin", "domain", "affiliate"}
        Con resolve=True gli shortener (amzn.to, a.co, ...) vengono risolti via rete.
        """
        urls = self.extract_links_from_message(message_text)
        amazon_urls = [u for u in urls if self.is_amazon_link(u)]

        results: List[Dict[str, str]] = []
        for url in amazon_urls:
            resolved = url
            if resolve and self.is_short_link(url):
                resolved = self.expand_url(url)

            asin = self.extract_asin(resolved)
            if not asin:
                continue

            domain = self.get_amazon_domain_from_url(resolved)
            affiliate = f"https://www.{domain}/dp/{asin}?tag={self.affiliate_tag}"
            results.append({
                "original": url,
                "resolved": resolved,
                "asin": asin,
                "domain": domain,
                "affiliate": affiliate,
            })
        return results

    def process_message(self, message_text: str, resolve: bool = False) -> Tuple[str, List[str]]:
        """
        Processa un messaggio e converte tutti i link Amazon in link affiliati.

        Args:
            message_text: testo del messaggio
            resolve: se True risolve gli shortener seguendo i redirect (richiede rete)

        Returns:
            tuple: (messaggio_modificato, lista_link_affiliati)
        """
        results = self.build_results(message_text, resolve=resolve)

        modified_message = message_text
        affiliate_links: List[str] = []
        for r in results:
            # Sostituisci il link originale (così com'era scritto) con quello affiliato
            modified_message = modified_message.replace(r["original"], r["affiliate"])
            affiliate_links.append(r["affiliate"])

        return modified_message, affiliate_links
