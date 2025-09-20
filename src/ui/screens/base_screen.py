"""
Écran de base pour tous les écrans de l'application
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

class BaseScreen(QWidget):
    """Classe de base pour tous les écrans"""
    
    screen_changed = pyqtSignal(str, dict)  # signal pour changer d'écran
    
    def __init__(self, config, locker_manager, payment_manager):
        super().__init__()
        self.config = config
        self.locker_manager = locker_manager
        self.payment_manager = payment_manager
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur de base"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
    
    def create_title(self, text: str) -> QLabel:
        """Crée un titre pour l'écran"""
        title = QLabel(text)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                margin: 20px 0;
                padding: 20px;
                background-color: #2d2d2d;
                border-radius: 12px;
            }
        """)
        return title
    
    def create_button(self, text: str, callback=None, style_class: str = "primary") -> QPushButton:
        """Crée un bouton stylisé"""
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 16, QFont.Bold))
        button.setMinimumHeight(60)
        
        if style_class == "primary":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 16px 32px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
        elif style_class == "secondary":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    color: white;
                    border: 2px solid #606060;
                    border-radius: 12px;
                    padding: 16px 32px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #303030;
                }
            """)
        elif style_class == "danger":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #d13438;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 16px 32px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b52d32;
                }
                QPushButton:pressed {
                    background-color: #9a252a;
                }
            """)
        
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def create_navigation_bar(self) -> QHBoxLayout:
        """Crée une barre de navigation"""
        nav_layout = QHBoxLayout()
        
        # Bouton retour
        back_button = self.create_button("← Retour", self.go_home, "secondary")
        back_button.setMaximumWidth(150)
        nav_layout.addWidget(back_button)
        
        nav_layout.addStretch()
        
        # Bouton admin (code secret)
        admin_button = self.create_button("Admin", self.go_admin, "secondary")
        admin_button.setMaximumWidth(100)
        nav_layout.addWidget(admin_button)
        
        return nav_layout
    
    def go_home(self):
        """Retourne à l'écran d'accueil"""
        self.screen_changed.emit('home', {})
    
    def go_admin(self):
        """Va à l'écran d'administration"""
        self.screen_changed.emit('admin', {})
    
    def refresh(self):
        """Rafraîchit l'écran (à surcharger dans les classes filles)"""
        pass
    
    def set_data(self, data: dict):
        """Définit les données pour l'écran (à surcharger dans les classes filles)"""
        pass