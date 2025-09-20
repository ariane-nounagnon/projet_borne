"""
Écran d'accueil de la borne
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from src.ui.screens.base_screen import BaseScreen

class HomeScreen(BaseScreen):
    """Écran d'accueil principal"""
    
    def __init__(self, config, locker_manager, payment_manager):
        super().__init__(config, locker_manager, payment_manager)
        
        # Timer pour l'animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(2000)  # 2 secondes
        self.animation_state = 0
    
    def setup_ui(self):
        """Configure l'interface de l'écran d'accueil"""
        super().setup_ui()
        
        # Titre de bienvenue
        welcome_title = QLabel("🔋 Bienvenue sur votre borne de recharge")
        welcome_title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("""
            QLabel {
                color: #0078d4;
                margin: 30px 0;
                padding: 30px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d2d2d, stop:0.5 #3d3d3d, stop:1 #2d2d2d);
                border-radius: 16px;
                border: 2px solid #0078d4;
            }
        """)
        self.layout.addWidget(welcome_title)
        
        # Informations sur les casiers disponibles
        self.status_frame = self._create_status_frame()
        self.layout.addWidget(self.status_frame)
        
        # Options principales
        options_layout = self._create_options_layout()
        self.layout.addLayout(options_layout)
        
        # Instructions
        instructions = self._create_instructions()
        self.layout.addWidget(instructions)
        
        self.layout.addStretch()
        
        # Barre de navigation
        nav_layout = self.create_navigation_bar()
        self.layout.addLayout(nav_layout)
    
    def _create_status_frame(self) -> QFrame:
        """Crée le cadre d'état des casiers"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 2px solid #404040;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Titre du statut
        status_title = QLabel("📊 État des casiers")
        status_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        status_title.setAlignment(Qt.AlignCenter)
        status_title.setStyleSheet("color: #ffffff; margin-bottom: 15px;")
        layout.addWidget(status_title)
        
        # Grille des casiers
        self.lockers_grid = QGridLayout()
        self._update_lockers_display()
        layout.addLayout(self.lockers_grid)
        
        return frame
    
    def _update_lockers_display(self):
        """Met à jour l'affichage des casiers"""
        # Nettoyer la grille existante
        for i in reversed(range(self.lockers_grid.count())):
            self.lockers_grid.itemAt(i).widget().setParent(None)
        
        # Afficher les casiers
        locker_count = self.config.get('lockers.count', 8)
        cols = 4
        
        for i in range(1, locker_count + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            
            is_available = self.locker_manager.is_locker_available(i)
            
            locker_widget = QLabel(f"Casier {i}")
            locker_widget.setAlignment(Qt.AlignCenter)
            locker_widget.setFont(QFont("Segoe UI", 12, QFont.Bold))
            locker_widget.setMinimumSize(120, 80)
            
            if is_available:
                locker_widget.setStyleSheet("""
                    QLabel {
                        background-color: #28a745;
                        color: white;
                        border-radius: 8px;
                        border: 2px solid #20c997;
                    }
                """)
                locker_widget.setText(f"🟢\nCasier {i}\nLIBRE")
            else:
                locker_widget.setStyleSheet("""
                    QLabel {
                        background-color: #dc3545;
                        color: white;
                        border-radius: 8px;
                        border: 2px solid #c82333;
                    }
                """)
                locker_widget.setText(f"🔴\nCasier {i}\nOCCUPÉ")
            
            self.lockers_grid.addWidget(locker_widget, row, col)
    
    def _create_options_layout(self) -> QVBoxLayout:
        """Crée le layout des options principales"""
        options_layout = QVBoxLayout()
        
        # Titre des options
        options_title = QLabel("🎯 Choisissez votre méthode d'accès")
        options_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        options_title.setAlignment(Qt.AlignCenter)
        options_title.setStyleSheet("color: #ffffff; margin: 20px 0;")
        options_layout.addWidget(options_title)
        
        # Grille des options
        options_grid = QGridLayout()
        
        # Option 1: Code prépayé
        prepaid_btn = self._create_option_button(
            "💳 Code Prépayé",
            "Utilisez un code acheté en boutique",
            self._go_to_prepaid_payment
        )
        options_grid.addWidget(prepaid_btn, 0, 0)
        
        # Option 2: Digicode personnel
        digicode_btn = self._create_option_button(
            "🔢 Digicode Personnel",
            "Choisissez votre code à 4 chiffres",
            self._go_to_digicode_selection
        )
        options_grid.addWidget(digicode_btn, 0, 1)
        
        # Option 3: QR Code
        qr_btn = self._create_option_button(
            "📱 Paiement QR",
            "Scannez pour payer à distance",
            self._go_to_qr_payment
        )
        options_grid.addWidget(qr_btn, 1, 0)
        
        # Option 4: USSD
        ussd_btn = self._create_option_button(
            "📞 Paiement USSD",
            "Payez depuis n'importe quel téléphone",
            self._go_to_ussd_payment
        )
        options_grid.addWidget(ussd_btn, 1, 1)
        
        options_layout.addLayout(options_grid)
        return options_layout
    
    def _create_option_button(self, title: str, description: str, callback) -> QPushButton:
        """Crée un bouton d'option stylisé"""
        button = QPushButton(f"{title}\n{description}")
        button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        button.setMinimumSize(300, 120)
        button.clicked.connect(callback)
        
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white;
                border: none;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                margin: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #004578);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #003d6b);
            }
        """)
        
        return button
    
    def _create_instructions(self) -> QLabel:
        """Crée le panneau d'instructions"""
        instructions = QLabel("""
        📋 INSTRUCTIONS D'UTILISATION:
        
        1️⃣ Choisissez votre méthode de paiement ci-dessus
        2️⃣ Sélectionnez un casier libre
        3️⃣ Placez votre appareil et fermez le casier
        4️⃣ Notez bien votre code pour récupérer votre appareil
        
        ⚡ Recharge solaire • 🔒 Sécurisé • 🌍 Écologique
        """)
        
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #cccccc;
                border-radius: 12px;
                padding: 25px;
                border: 2px solid #404040;
                line-height: 1.6;
            }
        """)
        
        return instructions
    
    def _go_to_prepaid_payment(self):
        """Va à l'écran de paiement par code prépayé"""
        self.screen_changed.emit('payment', {'method': 'prepaid'})
    
    def _go_to_digicode_selection(self):
        """Va à l'écran de sélection de digicode"""
        self.screen_changed.emit('locker', {'method': 'digicode'})
    
    def _go_to_qr_payment(self):
        """Va à l'écran de paiement QR"""
        self.screen_changed.emit('payment', {'method': 'qr'})
    
    def _go_to_ussd_payment(self):
        """Va à l'écran de paiement USSD"""
        self.screen_changed.emit('payment', {'method': 'ussd'})
    
    def _update_animation(self):
        """Met à jour l'animation de l'écran d'accueil"""
        self.animation_state = (self.animation_state + 1) % 3
        # Animation simple pour maintenir l'interface vivante
    
    def refresh(self):
        """Rafraîchit l'écran d'accueil"""
        self._update_lockers_display()
    
    def go_home(self):
        """Surcharge pour rester sur l'écran d'accueil"""
        self.refresh()