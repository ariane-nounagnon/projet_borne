"""
Fenêtre principale de l'application borne
"""

from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QVBoxLayout, 
                            QWidget, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from src.ui.screens.home_screen import HomeScreen
from src.ui.screens.payment_screen import PaymentScreen
from src.ui.screens.locker_screen import LockerScreen
from src.ui.screens.admin_screen import AdminScreen
from src.core.locker_manager import LockerManager
from src.core.payment_manager import PaymentManager
from src.core.logger import setup_logger

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = setup_logger("main_window")
        
        # Initialisation des gestionnaires
        self.locker_manager = LockerManager(config)
        self.payment_manager = PaymentManager(config)
        
        # Configuration de la fenêtre
        self.setWindowTitle("Borne de Recharge")
        self.setMinimumSize(800, 600)
        
        # Application du thème
        self._apply_theme()
        
        # Configuration de l'interface
        self._setup_ui()
        
        # Timer pour les vérifications périodiques
        self.timer = QTimer()
        self.timer.timeout.connect(self._periodic_checks)
        self.timer.start(30000)  # 30 secondes
        
        self.logger.info("Fenêtre principale initialisée")
    
    def _apply_theme(self):
        """Applique le thème sombre moderne"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 14px;
                min-height: 20px;
            }
            
            QLineEdit:focus {
                border-color: #0078d4;
            }
            
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
            }
        """)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget central avec pile d'écrans
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre de titre
        self._create_title_bar(layout)
        
        # Pile d'écrans
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Création des écrans
        self._create_screens()
        
        # Barre de statut
        self._create_status_bar(layout)
    
    def _create_title_bar(self, layout):
        """Crée la barre de titre"""
        title_frame = QWidget()
        title_frame.setFixedHeight(80)
        title_frame.setStyleSheet("""
            QWidget {
                background-color: #0078d4;
                border-radius: 0px;
            }
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # Titre principal
        title_label = QLabel("🔋 BORNE DE RECHARGE")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Indicateur de statut
        self.status_indicator = QLabel("🟢 OPÉRATIONNELLE")
        self.status_indicator.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.status_indicator.setStyleSheet("color: white;")
        title_layout.addWidget(self.status_indicator)
        
        layout.addWidget(title_frame)
    
    def _create_screens(self):
        """Crée tous les écrans de l'application"""
        # Écran d'accueil
        self.home_screen = HomeScreen(self.config, self.locker_manager, self.payment_manager)
        self.home_screen.screen_changed.connect(self.change_screen)
        self.stacked_widget.addWidget(self.home_screen)
        
        # Écran de paiement
        self.payment_screen = PaymentScreen(self.config, self.locker_manager, self.payment_manager)
        self.payment_screen.screen_changed.connect(self.change_screen)
        self.stacked_widget.addWidget(self.payment_screen)
        
        # Écran des casiers
        self.locker_screen = LockerScreen(self.config, self.locker_manager, self.payment_manager)
        self.locker_screen.screen_changed.connect(self.change_screen)
        self.stacked_widget.addWidget(self.locker_screen)
        
        # Écran d'administration
        self.admin_screen = AdminScreen(self.config, self.locker_manager, self.payment_manager)
        self.admin_screen.screen_changed.connect(self.change_screen)
        self.stacked_widget.addWidget(self.admin_screen)
        
        # Écran par défaut
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def _create_status_bar(self, layout):
        """Crée la barre de statut"""
        status_frame = QWidget()
        status_frame.setFixedHeight(40)
        status_frame.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 0px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 0, 20, 0)
        
        # Informations de statut
        self.locker_status_label = QLabel()
        self.locker_status_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        status_layout.addWidget(self.locker_status_label)
        
        status_layout.addStretch()
        
        # Heure
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        status_layout.addWidget(self.time_label)
        
        layout.addWidget(status_frame)
        
        # Mise à jour initiale
        self._update_status_bar()
    
    def _update_status_bar(self):
        """Met à jour la barre de statut"""
        from datetime import datetime
        
        # Mise à jour de l'heure
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
        # Mise à jour du statut des casiers
        available_lockers = len(self.locker_manager.get_available_lockers())
        total_lockers = self.config.get('lockers.count', 8)
        occupied_lockers = total_lockers - available_lockers
        
        self.locker_status_label.setText(
            f"Casiers: {available_lockers} libres / {occupied_lockers} occupés / {total_lockers} total"
        )
    
    def _periodic_checks(self):
        """Vérifications périodiques"""
        # Vérifier les sessions expirées
        self.locker_manager.check_expired_sessions()
        
        # Nettoyer les codes expirés
        self.payment_manager.cleanup_expired_codes()
        
        # Mettre à jour la barre de statut
        self._update_status_bar()
        
        # Rafraîchir l'écran actuel si nécessaire
        current_screen = self.stacked_widget.currentWidget()
        if hasattr(current_screen, 'refresh'):
            current_screen.refresh()
    
    def change_screen(self, screen_name: str, data: dict = None):
        """Change l'écran affiché"""
        screen_map = {
            'home': self.home_screen,
            'payment': self.payment_screen,
            'locker': self.locker_screen,
            'admin': self.admin_screen
        }
        
        if screen_name in screen_map:
            screen = screen_map[screen_name]
            
            # Passer les données à l'écran si nécessaire
            if data and hasattr(screen, 'set_data'):
                screen.set_data(data)
            
            # Rafraîchir l'écran
            if hasattr(screen, 'refresh'):
                screen.refresh()
            
            self.stacked_widget.setCurrentWidget(screen)
            self.logger.info(f"Changement d'écran vers: {screen_name}")
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        self.logger.info("Fermeture de l'application")
        self.timer.stop()
        event.accept()