"""
Gestionnaire des paiements et codes prépayés
"""

import json
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from src.core.logger import setup_logger

@dataclass
class PrepaidCode:
    """Représente un code prépayé"""
    code: str
    value: float
    created_date: datetime
    expiry_date: datetime
    is_used: bool = False
    used_date: Optional[datetime] = None

class PaymentManager:
    """Gestionnaire des paiements et codes prépayés"""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("payment_manager")
        self.codes_file = "data/prepaid_codes.json"
        
        # Création du dossier data
        os.makedirs("data", exist_ok=True)
        
        self.prepaid_codes = {}
        self._load_prepaid_codes()
    
    def _load_prepaid_codes(self):
        """Charge les codes prépayés depuis le fichier"""
        if os.path.exists(self.codes_file):
            try:
                with open(self.codes_file, 'r', encoding='utf-8') as f:
                    codes_data = json.load(f)
                    
                for code_data in codes_data:
                    code = PrepaidCode(
                        code=code_data['code'],
                        value=code_data['value'],
                        created_date=datetime.fromisoformat(code_data['created_date']),
                        expiry_date=datetime.fromisoformat(code_data['expiry_date']),
                        is_used=code_data.get('is_used', False),
                        used_date=datetime.fromisoformat(code_data['used_date']) if code_data.get('used_date') else None
                    )
                    self.prepaid_codes[code.code] = code
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des codes prépayés: {e}")
    
    def _save_prepaid_codes(self):
        """Sauvegarde les codes prépayés"""
        try:
            codes_data = []
            for code in self.prepaid_codes.values():
                code_dict = asdict(code)
                code_dict['created_date'] = code.created_date.isoformat()
                code_dict['expiry_date'] = code.expiry_date.isoformat()
                if code.used_date:
                    code_dict['used_date'] = code.used_date.isoformat()
                codes_data.append(code_dict)
            
            with open(self.codes_file, 'w', encoding='utf-8') as f:
                json.dump(codes_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des codes prépayés: {e}")
    
    def generate_prepaid_code(self, value: float, validity_days: int = 365) -> str:
        """Génère un nouveau code prépayé"""
        code_length = self.config.get('payment.prepaid_code_length', 8)
        
        # Générer un code unique
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(code_length))
            if code not in self.prepaid_codes:
                break
        
        # Créer le code prépayé
        prepaid_code = PrepaidCode(
            code=code,
            value=value,
            created_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=validity_days)
        )
        
        self.prepaid_codes[code] = prepaid_code
        self._save_prepaid_codes()
        
        self.logger.info(f"Code prépayé généré: {code} (valeur: {value}€)")
        return code
    
    def validate_prepaid_code(self, code: str) -> Optional[PrepaidCode]:
        """Valide un code prépayé"""
        if code not in self.prepaid_codes:
            self.logger.warning(f"Code prépayé inexistant: {code}")
            return None
        
        prepaid_code = self.prepaid_codes[code]
        
        # Vérifier si le code est déjà utilisé
        if prepaid_code.is_used:
            self.logger.warning(f"Code prépayé déjà utilisé: {code}")
            return None
        
        # Vérifier si le code est expiré
        if datetime.now() > prepaid_code.expiry_date:
            self.logger.warning(f"Code prépayé expiré: {code}")
            return None
        
        return prepaid_code
    
    def use_prepaid_code(self, code: str) -> bool:
        """Utilise un code prépayé"""
        prepaid_code = self.validate_prepaid_code(code)
        if not prepaid_code:
            return False
        
        # Marquer le code comme utilisé
        prepaid_code.is_used = True
        prepaid_code.used_date = datetime.now()
        
        self._save_prepaid_codes()
        self.logger.info(f"Code prépayé utilisé: {code}")
        return True
    
    def get_code_value(self, code: str) -> float:
        """Récupère la valeur d'un code prépayé"""
        prepaid_code = self.validate_prepaid_code(code)
        return prepaid_code.value if prepaid_code else 0.0
    
    def generate_qr_payment_url(self, amount: float, reference: str) -> str:
        """Génère une URL de paiement QR"""
        base_url = self.config.get('payment.qr_payment_url', 'https://payment.example.com')
        return f"{base_url}?amount={amount}&ref={reference}"
    
    def get_ussd_code(self) -> str:
        """Récupère le code USSD pour le paiement"""
        return self.config.get('payment.ussd_code', '*123#')
    
    def cleanup_expired_codes(self):
        """Nettoie les codes expirés"""
        current_time = datetime.now()
        expired_codes = []
        
        for code, prepaid_code in self.prepaid_codes.items():
            if current_time > prepaid_code.expiry_date:
                expired_codes.append(code)
        
        for code in expired_codes:
            del self.prepaid_codes[code]
            self.logger.info(f"Code prépayé expiré supprimé: {code}")
        
        if expired_codes:
            self._save_prepaid_codes()