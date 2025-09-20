"""
Gestionnaire des casiers de la borne
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from src.core.logger import setup_logger

@dataclass
class LockerSession:
    """Représente une session d'utilisation d'un casier"""
    locker_id: int
    user_code: str
    start_time: datetime
    end_time: Optional[datetime] = None
    payment_method: str = ""
    amount_paid: float = 0.0
    is_active: bool = True

class LockerManager:
    """Gestionnaire des casiers et des sessions"""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("locker_manager")
        self.sessions_file = "data/sessions.json"
        self.lockers_file = "data/lockers.json"
        
        # Création du dossier data
        os.makedirs("data", exist_ok=True)
        
        # État des casiers (True = occupé, False = libre)
        self.lockers_status = {}
        self.active_sessions = {}
        
        self._initialize_lockers()
        self._load_sessions()
    
    def _initialize_lockers(self):
        """Initialise l'état des casiers"""
        locker_count = self.config.get('lockers.count', 8)
        
        if os.path.exists(self.lockers_file):
            try:
                with open(self.lockers_file, 'r', encoding='utf-8') as f:
                    self.lockers_status = json.load(f)
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des casiers: {e}")
        
        # Initialiser les casiers manquants
        for i in range(1, locker_count + 1):
            if str(i) not in self.lockers_status:
                self.lockers_status[str(i)] = False
    
    def _load_sessions(self):
        """Charge les sessions actives"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    
                for session_data in sessions_data:
                    if session_data.get('is_active', False):
                        session = LockerSession(
                            locker_id=session_data['locker_id'],
                            user_code=session_data['user_code'],
                            start_time=datetime.fromisoformat(session_data['start_time']),
                            end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                            payment_method=session_data.get('payment_method', ''),
                            amount_paid=session_data.get('amount_paid', 0.0),
                            is_active=session_data.get('is_active', True)
                        )
                        self.active_sessions[session.locker_id] = session
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des sessions: {e}")
    
    def _save_sessions(self):
        """Sauvegarde les sessions"""
        try:
            sessions_data = []
            for session in self.active_sessions.values():
                session_dict = asdict(session)
                session_dict['start_time'] = session.start_time.isoformat()
                if session.end_time:
                    session_dict['end_time'] = session.end_time.isoformat()
                sessions_data.append(session_dict)
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des sessions: {e}")
    
    def _save_lockers_status(self):
        """Sauvegarde l'état des casiers"""
        try:
            with open(self.lockers_file, 'w', encoding='utf-8') as f:
                json.dump(self.lockers_status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des casiers: {e}")
    
    def get_available_lockers(self) -> List[int]:
        """Retourne la liste des casiers disponibles"""
        return [int(locker_id) for locker_id, is_occupied in self.lockers_status.items() 
                if not is_occupied]
    
    def is_locker_available(self, locker_id: int) -> bool:
        """Vérifie si un casier est disponible"""
        return not self.lockers_status.get(str(locker_id), True)
    
    def reserve_locker(self, locker_id: int, user_code: str, payment_method: str = "", amount: float = 0.0) -> bool:
        """Réserve un casier pour un utilisateur"""
        if not self.is_locker_available(locker_id):
            return False
        
        # Créer une nouvelle session
        session = LockerSession(
            locker_id=locker_id,
            user_code=user_code,
            start_time=datetime.now(),
            payment_method=payment_method,
            amount_paid=amount
        )
        
        # Marquer le casier comme occupé
        self.lockers_status[str(locker_id)] = True
        self.active_sessions[locker_id] = session
        
        # Sauvegarder
        self._save_lockers_status()
        self._save_sessions()
        
        self.logger.info(f"Casier {locker_id} réservé avec le code {user_code}")
        return True
    
    def unlock_locker(self, locker_id: int, code: str) -> bool:
        """Déverrouille un casier avec un code"""
        # Vérifier le code maître
        master_code = self.config.get('security.master_code', '9999')
        if code == master_code:
            self.logger.info(f"Casier {locker_id} ouvert avec le code maître")
            return True
        
        # Vérifier le code utilisateur
        if locker_id in self.active_sessions:
            session = self.active_sessions[locker_id]
            if session.user_code == code and session.is_active:
                self.logger.info(f"Casier {locker_id} ouvert avec le code utilisateur")
                return True
        
        self.logger.warning(f"Tentative d'ouverture échouée pour le casier {locker_id}")
        return False
    
    def release_locker(self, locker_id: int) -> bool:
        """Libère un casier"""
        if locker_id in self.active_sessions:
            session = self.active_sessions[locker_id]
            session.end_time = datetime.now()
            session.is_active = False
            
            # Marquer le casier comme libre
            self.lockers_status[str(locker_id)] = False
            
            # Supprimer de la liste des sessions actives
            del self.active_sessions[locker_id]
            
            # Sauvegarder
            self._save_lockers_status()
            self._save_sessions()
            
            self.logger.info(f"Casier {locker_id} libéré")
            return True
        
        return False
    
    def get_session_info(self, locker_id: int) -> Optional[LockerSession]:
        """Récupère les informations d'une session"""
        return self.active_sessions.get(locker_id)
    
    def check_expired_sessions(self):
        """Vérifie et gère les sessions expirées"""
        timeout = self.config.get('security.session_timeout', 300)
        current_time = datetime.now()
        expired_sessions = []
        
        for locker_id, session in self.active_sessions.items():
            if (current_time - session.start_time).seconds > timeout:
                expired_sessions.append(locker_id)
        
        for locker_id in expired_sessions:
            self.logger.warning(f"Session expirée pour le casier {locker_id}")
            self.release_locker(locker_id)