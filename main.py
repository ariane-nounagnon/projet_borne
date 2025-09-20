#!/usr/bin/env python3
"""
Application principale de la borne de recharge
Point d'entrée de l'application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow
from src.core.config import Config
from src.core.logger import setup_logger

def main():
    """Point d'entrée principal de l'application"""
    # Configuration de l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Borne de Recharge")
    app.setApplicationVersion("1.0.0")
    
    # Configuration pour écran tactile
    app.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    
    # Configuration du logger
    logger = setup_logger()
    logger.info("Démarrage de l'application borne de recharge")
    
    # Chargement de la configuration
    config = Config()
    
    # Création et affichage de la fenêtre principale
    window = MainWindow(config)
    
    # Mode plein écran pour la borne
    if config.get('display.fullscreen', True):
        window.showFullScreen()
    else:
        window.show()
    
    # Démarrage de l'application
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()