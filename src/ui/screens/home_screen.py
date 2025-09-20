from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton
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
        """Configure l'interface de l'écran d'accueil"""
        super().setup_ui()
        self.layout.setContentsMargins(18, 10, 18, 10)
        self.layout.setSpacing(14)

        # Titre de bienvenue
        welcome_title = QLabel("🔋 Bienvenue sur votre borne de recharge")
        welcome_title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("color: #0078d4; margin-bottom: 8px;")
        welcome_title.setMaximumHeight(36)
        self.layout.addWidget(welcome_title)

        # Etat des casiers
        self.status_frame = self._create_status_frame()
        self.status_frame.setMaximumHeight(70)
        self.layout.addWidget(self.status_frame)

        self.layout.addSpacing(7)

        # Options principales
        options_layout = self._create_options_layout()
        self.layout.addLayout(options_layout)
        self.layout.addSpacing(7)

        # Instructions
        instructions = self._create_instructions()
        instructions.setMaximumHeight(62)
        self.layout.addWidget(instructions)

        self.layout.addStretch()

        # Barre de navigation
        nav_layout = self.create_navigation_bar()
        self.layout.addLayout(nav_layout)

    def _create_status_frame(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 2px solid #404040;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)
        status_title = QLabel("📊 État des casiers")
        status_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        status_title.setAlignment(Qt.AlignCenter)
        status_title.setStyleSheet("color: #ffffff; margin-bottom: 2px;")
        layout.addWidget(status_title)
        self.lockers_grid = QGridLayout()
        self.lockers_grid.setSpacing(4)
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
            locker_widget.setFixedSize(72, 29)
            if is_available:
                locker_widget.setStyleSheet(
                    "background-color: #28a745; color: white; border-radius: 6px; border: 2px solid #20c997;")
                locker_widget.setText(f"🟢 C{i}\nLIBRE")
            else:
                locker_widget.setStyleSheet(
                    "background-color: #dc3545; color: white; border-radius: 6px; border: 2px solid #c82333;")
                locker_widget.setText(f"🔴 C{i}\nOCCUPÉ")
            self.lockers_grid.addWidget(locker_widget, row, col)

    def _create_options_layout(self) -> QVBoxLayout:
        options_layout = QVBoxLayout()
        options_layout.setSpacing(7)
        options_title = QLabel("🎯 Choisissez votre méthode d'accès")
        options_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        options_title.setAlignment(Qt.AlignCenter)
        options_title.setStyleSheet("color: #ffffff; margin-bottom: 3px;")
        options_layout.addWidget(options_title)
        options_grid = QGridLayout()
        options_grid.setSpacing(6)
        prepaid_btn = self._create_option_button("💳 Code Prépayé", "Code boutique", self._go_to_prepaid_payment)
        digicode_btn = self._create_option_button("🔢 Digicode Perso", "Code 4 chiffres", self._go_to_digicode_selection)
        qr_btn = self._create_option_button("📱 Paiement QR", "Payez à distance", self._go_to_qr_payment)
        ussd_btn = self._create_option_button("📞 Paiement USSD", "Payez téléphone", self._go_to_ussd_payment)
        options_grid.addWidget(prepaid_btn, 0, 0)
        options_grid.addWidget(digicode_btn, 0, 1)
        options_grid.addWidget(qr_btn, 1, 0)
        options_grid.addWidget(ussd_btn, 1, 1)
        options_layout.addLayout(options_grid)
        return options_layout

    def _create_option_button(self, title, description, callback):
        button = QPushButton(f"{title}\n{description}")
        button.setFont(QFont("Segoe UI", 9, QFont.Bold))
        button.setMinimumSize(84, 36)
        button.setMaximumSize(110, 46)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white; border: none; border-radius: 8px; padding: 4px; margin: 2px;
            }
        """)
        return button

    def _create_instructions(self) -> QLabel:
        instructions = QLabel(
            "📋 INSTRUCTIONS:\n"
            "1️⃣ Choisissez un mode\n"
            "2️⃣ Sélectionnez un casier\n"
            "3️⃣ Placez votre appareil\n"
            "4️⃣ Notez votre code\n"
            "⚡ Recharge solaire • 🔒 Sécurisé")
        instructions.setFont(QFont("Segoe UI", 8))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet(
            "background-color: #2d2d2d; color: #cccccc; border-radius: 7px; padding: 3px; border: 2px solid #404040;"
        )
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
