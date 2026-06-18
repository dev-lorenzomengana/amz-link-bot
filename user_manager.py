import json
import os
import tempfile
from typing import Optional, Dict, Any
from datetime import datetime

class UserManager:
    """Gestisce le configurazioni degli utenti del bot."""
    
    def __init__(self, data_file: str = "user_data.json"):
        self.data_file = data_file
        self.users_data = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """Carica i dati degli utenti dal file JSON."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                # Se il file è corrotto, inizia con dati vuoti
                return {}
        return {}
    
    def _save_data(self):
        """Salva i dati degli utenti nel file JSON in modo atomico (temp + replace)."""
        try:
            directory = os.path.dirname(os.path.abspath(self.data_file)) or '.'
            fd, tmp_path = tempfile.mkstemp(suffix='.tmp', dir=directory)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self.users_data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                # os.replace è atomico sullo stesso filesystem: niente file mezzo scritto
                os.replace(tmp_path, self.data_file)
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
        except Exception as e:
            print(f"Errore nel salvare i dati utente: {e}")
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Ottiene i dati di un utente."""
        user_id_str = str(user_id)
        if user_id_str not in self.users_data:
            # Crea un nuovo utente con dati predefiniti
            self.users_data[user_id_str] = {
                "affiliate_tag": None,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "total_conversions": 0,
                "is_configured": False
            }
            self._save_data()
        
        # Aggiorna ultima attività
        self.users_data[user_id_str]["last_activity"] = datetime.now().isoformat()
        return self.users_data[user_id_str]
    
    def set_affiliate_tag(self, user_id: int, affiliate_tag: str) -> bool:
        """Imposta il tag affiliato per un utente."""
        if not self.validate_affiliate_tag(affiliate_tag):
            return False
        
        user_data = self.get_user_data(user_id)
        user_data["affiliate_tag"] = affiliate_tag.strip()
        user_data["is_configured"] = True
        user_data["configured_at"] = datetime.now().isoformat()
        
        self._save_data()
        return True
    
    def get_affiliate_tag(self, user_id: int) -> Optional[str]:
        """Ottiene il tag affiliato di un utente."""
        user_data = self.get_user_data(user_id)
        return user_data.get("affiliate_tag")
    
    def is_user_configured(self, user_id: int) -> bool:
        """Verifica se l'utente ha configurato il tag affiliato."""
        user_data = self.get_user_data(user_id)
        return user_data.get("is_configured", False) and user_data.get("affiliate_tag") is not None
    
    def increment_conversions(self, user_id: int, count: int = 1):
        """Incrementa il contatore delle conversioni per un utente."""
        user_data = self.get_user_data(user_id)
        user_data["total_conversions"] = user_data.get("total_conversions", 0) + count
        self._save_data()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Ottiene le statistiche di un utente."""
        user_data = self.get_user_data(user_id)
        return {
            "total_conversions": user_data.get("total_conversions", 0),
            "created_at": user_data.get("created_at"),
            "last_activity": user_data.get("last_activity"),
            "is_configured": user_data.get("is_configured", False),
            "affiliate_tag": user_data.get("affiliate_tag", "Non configurato")
        }
    
    def get_all_users_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche generali di tutti gli utenti (per admin)."""
        total_users = len(self.users_data)
        configured_users = sum(1 for user in self.users_data.values() if user.get("is_configured", False))
        total_conversions = sum(user.get("total_conversions", 0) for user in self.users_data.values())
        
        return {
            "total_users": total_users,
            "configured_users": configured_users,
            "unconfigured_users": total_users - configured_users,
            "total_conversions": total_conversions,
            "average_conversions": total_conversions / total_users if total_users > 0 else 0
        }
    
    def validate_affiliate_tag(self, tag: str) -> bool:
        """Valida un tag affiliato Amazon."""
        if not tag or not isinstance(tag, str):
            return False
        
        tag = tag.strip()
        
        # Controlli di base
        if len(tag) < 3 or len(tag) > 50:
            return False
        
        # Caratteri validi (lettere, numeri, trattini)
        import re
        if not re.match(r'^[a-zA-Z0-9\-_]+$', tag):
            return False
        
        # Non può iniziare o finire con trattino
        if tag.startswith('-') or tag.endswith('-'):
            return False
        
        return True
    
    def delete_user_data(self, user_id: int) -> bool:
        """Elimina i dati di un utente."""
        user_id_str = str(user_id)
        if user_id_str in self.users_data:
            del self.users_data[user_id_str]
            self._save_data()
            return True
        return False
    
    def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Esporta tutti i dati di un utente (per GDPR)."""
        return self.get_user_data(user_id)
    
    def get_recent_users(self, days: int = 7) -> int:
        """Ottiene il numero di utenti attivi negli ultimi X giorni."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_users = 0
        
        for user_data in self.users_data.values():
            last_activity = user_data.get("last_activity")
            if last_activity:
                try:
                    activity_date = datetime.fromisoformat(last_activity)
                    if activity_date > cutoff_date:
                        recent_users += 1
                except:
                    continue
        
        return recent_users