"""
Gestionnaire de configuration de l'application
"""

import json
import os
from typing import Any, Dict

class Config:
    """Gestionnaire de configuration centralisé"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            "display": {
                "fullscreen": True,
                "width": 1024,
                "height": 768,
                "language": "fr"
            },
            "security": {
                "master_code": "9999",
                "session_timeout": 300,  # 5 minutes
                "max_attempts": 3
            },
            "lockers": {
                "count": 8,
                "charging_time_limit": 7200  # 2 heures
            },
            "payment": {
                "prepaid_code_length": 8,
                "ussd_code": "*123#",
                "qr_payment_url": "https://payment.example.com"
            },
            "hardware": {
                "gpio_enabled": False,  # True sur Raspberry Pi
                "touchscreen": True
            }
        }
    
    def _load_config(self):
        """Charge la configuration depuis le fichier"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Fusionne la configuration du fichier avec la configuration par défaut"""
        def merge_dict(default: dict, override: dict):
            for key, value in override.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dict(default[key], value)
                else:
                    default[key] = value
        
        merge_dict(self._config, file_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration avec notation pointée"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Définit une valeur de configuration"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Sauvegarde la configuration dans le fichier"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")