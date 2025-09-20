from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from src.ui.screens.base_screen import BaseScreen

class HomeScreen(BaseScreen):
    """Écran d'accueil principal"""

    def __init__(self, config, locker_manager, payment_manager):
        super().__init__(config, locker_manager, payment_manager)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(2000)
        self.animation_state = 0

    def setup_ui(self):
        super().setup_ui()
        # Conteneur principal pour le scroll (responsive)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(24, 16, 24, 16)
        scroll_layout.setSpacing(18)

        # Titre bien centré
        welcome_title = QLabel("🔋 Bienvenue sur votre borne de recharge")
        welcome_title.setFont(QFont("Segoe UI", 19, QFont.Bold))
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("color: #0078d4; margin-bottom: 4px;")
        scroll_layout.addWidget(welcome_title)

        # Cadre état des casiers
        self.status_frame = self._create_status_frame()
        self.status_frame.setMaximumHeight(82)
        scroll_layout.addWidget(self.status_frame)

        # Espacement léger
        scroll_layout.addSpacing(5)

        # Bloc options
        options_layout = self._create_options_layout()
        scroll_layout.addLayout(options_layout)

        # Instructions, petits caractères et marge compacte
        instructions = self._create_instructions()
        instructions.setMaximumHeight(46)
        scroll_layout.addWidget(instructions)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)

        # Barre de navigation en bas (en-dehors du scroll pour rester visible)
        nav_layout = self.create_navigation_bar()
        self.layout.addLayout(nav_layout)

    def _create_status_frame(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 7px;
                border: 1px solid #404040;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(2)
        status_title = QLabel("📊 État des casiers")
        status_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        status_title.setAlignment(Qt.AlignCenter)
        status_title.setStyleSheet("color: #ffffff;")
        layout.addWidget(status_title)
        self.lockers_grid = QGridLayout()
        self.lockers_grid.setSpacing(3)
        self._update_lockers_display()
        layout.addLayout(self.lockers_grid)
        return frame

    def _update_lockers_display(self):
        for i in reversed(range(self.lockers_grid.count())):
            widget = self.lockers_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        locker_count = self.config.get('lockers.count', 8)
        cols = 4
        for i in range(1, locker_count + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            is_available = self.locker_manager.is_locker_available(i)
            locker_widget = QLabel(f"Casier {i}")
            locker_widget.setAlignment(Qt.AlignCenter)
            locker_widget.setFont(QFont("Segoe UI", 8, QFont.Bold))
            locker_widget.setFixedSize(63, 24)
            if is_available:
                locker_widget.setStyleSheet(
                    "background-color: #28a745; color: white; border-radius: 5px; border: 1px solid #20c997;")
                locker_widget.setText(f"🟢 C{i}\nLIBRE")
            else:
                locker_widget.setStyleSheet(
                    "background-color: #dc3545; color: white; border-radius: 5px; border: 1px solid #c82333;")
                locker_widget.setText(f"🔴 C{i}\nOCCUPÉ")
            self.lockers_grid.addWidget(locker_widget, row, col)

    def _create_options_layout(self) -> QVBoxLayout:
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        options_title = QLabel("🎯 Choisissez votre méthode d'accès")
        options_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        options_title.setAlignment(Qt.AlignCenter)
        options_title.setStyleSheet("color: #ffffff; margin-bottom: 2px;")
        options_layout.addWidget(options_title)
        # Deux lignes, boutons larges et compacts
        options_grid = QGridLayout()
        options_grid.setSpacing(7)
        prepaid_btn = self._create_option_button("💳 Code Prépayé", "Code boutique", self._go_to_prepaid_payment)
        digicode_btn = self._create_option_button("🔢 Digicode Perso", "4 chiffres", self._go_to_digicode_selection)
        qr_btn = self._create_option_button("📱 Paiement QR", "A distance", self._go_to_qr_payment)
        ussd_btn = self._create_option_button("📞 Paiement USSD", "Tél simple", self._go_to_ussd_payment)
        options_grid.addWidget(prepaid_btn, 0, 0)
        options_grid.addWidget(digicode_btn, 0, 1)
        options_grid.addWidget(qr_btn, 1, 0)
        options_grid.addWidget(ussd_btn, 1, 1)
        options_layout.addLayout(options_grid)
        return options_layout

    def _create_option_button(self, title, description, callback):
        button = QPushButton(f"{title}\n{description}")
        button.setFont(QFont("Segoe UI", 8, QFont.Bold))
        button.setMinimumSize(110, 46)
        button.setMaximumSize(145, 56)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white; border: none; border-radius: 7px; padding: 2px 2px;
            }
        """)
        return button

    def _create_instructions(self) -> QLabel:
        instructions = QLabel(
            "📋 INSTRUCTIONS:\n"
            "1️⃣ Choisir un mode   2️⃣ Prendre un casier   3️⃣ Placer l'appareil   4️⃣ Garder le code")
        instructions.setFont(QFont("Segoe UI", 7))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet(
            "background-color: #2d2d2d; color: #cccccc; border-radius: 5px; padding: 2px; border: 1px solid #404040;")
        return instructions

    def _go_to_prepaid_payment(self):
        self.screen_changed.emit('payment', {'method': 'prepaid'})
    def _go_to_digicode_selection(self):
        self.screen_changed.emit('locker', {'method': 'digicode'})
    def _go_to_qr_payment(self):
        self.screen_changed.emit('payment', {'method': 'qr'})
    def _go_to_ussd_payment(self):
        self.screen_changed.emit('payment', {'method': 'ussd'})
    def _update_animation(self):
        self.animation_state = (self.animation_state + 1) % 3
    def refresh(self):
        self._update_lockers_display()
    def go_home(self):
        self.refresh()
