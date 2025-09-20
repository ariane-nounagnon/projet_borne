"""
Écran de paiement de la borne
"""

import qrcode
from io import BytesIO
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFrame, QTextEdit, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from src.ui.screens.base_screen import BaseScreen

class PaymentScreen(BaseScreen):
    """Écran de gestion des paiements"""
    
    def __init__(self, config, locker_manager, payment_manager):
        super().__init__(config, locker_manager, payment_manager)
        self.payment_method = 'prepaid'
        self.payment_data = {}
    
    def setup_ui(self):
        """Configure l'interface de l'écran de paiement"""
        super().setup_ui()
        
        # Titre
        self.title_label = self.create_title("💳 Paiement")
        self.layout.addWidget(self.title_label)
        
        # Zone de contenu principal
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 2px solid #404040;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.layout.addWidget(self.content_frame)
        
        # Zone de message
        self.message_label = QLabel()
        self.message_label.setFont(QFont("Segoe UI", 16))
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        self.layout.addWidget(self.message_label)
        
        self.layout.addStretch()
        
        # Barre de navigation
        nav_layout = self.create_navigation_bar()
        self.layout.addLayout(nav_layout)
    
    def set_data(self, data: dict):
        """Configure l'écran selon la méthode de paiement"""
        self.payment_data = data
        self.payment_method = data.get('method', 'prepaid')
        
        # Nettoyer le contenu existant
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Configurer selon la méthode
        if self.payment_method == 'prepaid':
            self._setup_prepaid_payment()
        elif self.payment_method == 'qr':
            self._setup_qr_payment()
        elif self.payment_method == 'ussd':
            self._setup_ussd_payment()
    
    def _setup_prepaid_payment(self):
        """Configure l'interface pour le paiement par code prépayé"""
        self.title_label.setText("💳 Paiement par Code Prépayé")
        
        # Instructions
        instructions = QLabel("""
        🎫 Entrez votre code prépayé acheté en boutique
        
        Le code contient 8 caractères (lettres et chiffres)
        Exemple: AB12CD34
        """)
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(instructions)
        
        # Champ de saisie du code
        code_layout = QHBoxLayout()
        
        code_label = QLabel("Code prépayé:")
        code_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        code_label.setStyleSheet("color: #ffffff;")
        code_layout.addWidget(code_label)
        
        self.code_input = QLineEdit()
        self.code_input.setFont(QFont("Segoe UI", 16))
        self.code_input.setPlaceholderText("Entrez votre code...")
        self.code_input.setMaxLength(8)
        self.code_input.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 18px;
                text-transform: uppercase;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        self.code_input.textChanged.connect(self._on_code_changed)
        code_layout.addWidget(self.code_input)
        
        self.content_layout.addLayout(code_layout)
        
        # Bouton de validation
        self.validate_button = self.create_button(
            "✅ Valider le code", 
            self._validate_prepaid_code
        )
        self.validate_button.setEnabled(False)
        self.content_layout.addWidget(self.validate_button)
        
        # Clavier virtuel
        self._create_virtual_keyboard()
    
    def _setup_qr_payment(self):
        """Configure l'interface pour le paiement QR"""
        self.title_label.setText("📱 Paiement par QR Code")
        
        # Instructions
        instructions = QLabel("""
        📱 Scannez le QR code avec votre téléphone
        
        Vous serez redirigé vers la page de paiement
        Une fois le paiement effectué, votre casier s'ouvrira automatiquement
        """)
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(instructions)
        
        # Génération et affichage du QR code
        self._generate_qr_code()
        
        # Bouton de rafraîchissement
        refresh_button = self.create_button(
            "🔄 Nouveau QR Code", 
            self._generate_qr_code,
            "secondary"
        )
        self.content_layout.addWidget(refresh_button)
    
    def _setup_ussd_payment(self):
        """Configure l'interface pour le paiement USSD"""
        self.title_label.setText("📞 Paiement par USSD")
        
        # Instructions
        ussd_code = self.payment_manager.get_ussd_code()
        instructions = QLabel(f"""
        📞 Composez le code USSD suivant sur votre téléphone:
        
        {ussd_code}
        
        Suivez les instructions sur votre téléphone pour effectuer le paiement
        Une fois le paiement confirmé, appuyez sur "Paiement effectué"
        """)
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(instructions)
        
        # Code USSD en grand
        ussd_display = QLabel(ussd_code)
        ussd_display.setFont(QFont("Segoe UI", 36, QFont.Bold))
        ussd_display.setAlignment(Qt.AlignCenter)
        ussd_display.setStyleSheet("""
            QLabel {
                color: #0078d4;
                background-color: #404040;
                border-radius: 12px;
                padding: 30px;
                border: 3px solid #0078d4;
            }
        """)
        self.content_layout.addWidget(ussd_display)
        
        # Bouton de confirmation
        confirm_button = self.create_button(
            "✅ Paiement effectué", 
            self._confirm_ussd_payment
        )
        self.content_layout.addWidget(confirm_button)
    
    def _create_virtual_keyboard(self):
        """Crée un clavier virtuel pour la saisie tactile"""
        keyboard_frame = QFrame()
        keyboard_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 8px;
                margin-top: 20px;
            }
        """)
        
        keyboard_layout = QGridLayout(keyboard_frame)
        
        # Touches du clavier
        keys = [
            ['1', '2', '3', '4', '5'],
            ['6', '7', '8', '9', '0'],
            ['A', 'B', 'C', 'D', 'E'],
            ['F', 'G', 'H', 'I', 'J'],
            ['K', 'L', 'M', 'N', 'O'],
            ['P', 'Q', 'R', 'S', 'T'],
            ['U', 'V', 'W', 'X', 'Y'],
            ['Z', '⌫', '🔄', '✅', '']
        ]
        
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                if key:
                    button = QPushButton(key)
                    button.setFont(QFont("Segoe UI", 14, QFont.Bold))
                    button.setMinimumSize(60, 50)
                    
                    if key == '⌫':
                        button.clicked.connect(self._backspace)
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #d13438;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #b52d32;
                            }
                        """)
                    elif key == '🔄':
                        button.clicked.connect(self._clear_input)
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #ffc107;
                                color: black;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #e0a800;
                            }
                        """)
                    elif key == '✅':
                        button.clicked.connect(self._validate_prepaid_code)
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #28a745;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #218838;
                            }
                        """)
                    else:
                        button.clicked.connect(lambda checked, k=key: self._add_character(k))
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #606060;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #707070;
                            }
                        """)
                    
                    keyboard_layout.addWidget(button, row, col)
        
        self.content_layout.addWidget(keyboard_frame)
    
    def _add_character(self, char: str):
        """Ajoute un caractère au champ de saisie"""
        current_text = self.code_input.text()
        if len(current_text) < 8:
            self.code_input.setText(current_text + char)
    
    def _backspace(self):
        """Supprime le dernier caractère"""
        current_text = self.code_input.text()
        self.code_input.setText(current_text[:-1])
    
    def _clear_input(self):
        """Efface le champ de saisie"""
        self.code_input.clear()
    
    def _on_code_changed(self, text: str):
        """Gère le changement de texte dans le champ de code"""
        # Convertir en majuscules
        text = text.upper()
        self.code_input.setText(text)
        
        # Activer/désactiver le bouton de validation
        self.validate_button.setEnabled(len(text) == 8)
    
    def _validate_prepaid_code(self):
        """Valide le code prépayé"""
        code = self.code_input.text().strip()
        
        if len(code) != 8:
            self._show_message("❌ Le code doit contenir exactement 8 caractères", "error")
            return
        
        # Vérifier le code
        prepaid_code = self.payment_manager.validate_prepaid_code(code)
        
        if prepaid_code:
            # Code valide, aller à la sélection de casier
            self._show_message(f"✅ Code valide! Valeur: {prepaid_code.value}€", "success")
            
            # Utiliser le code
            if self.payment_manager.use_prepaid_code(code):
                # Aller à la sélection de casier
                QTimer.singleShot(2000, lambda: self.screen_changed.emit('locker', {
                    'method': 'prepaid',
                    'code': code,
                    'amount': prepaid_code.value
                }))
        else:
            self._show_message("❌ Code invalide, expiré ou déjà utilisé", "error")
    
    def _generate_qr_code(self):
        """Génère et affiche un QR code pour le paiement"""
        import uuid
        
        # Générer une référence unique
        reference = str(uuid.uuid4())[:8].upper()
        amount = 5.0  # Prix fixe pour l'exemple
        
        # Générer l'URL de paiement
        payment_url = self.payment_manager.generate_qr_payment_url(amount, reference)
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        # Convertir en image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir pour Qt
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        
        # Afficher le QR code
        if hasattr(self, 'qr_label'):
            self.qr_label.setParent(None)
        
        self.qr_label = QLabel()
        self.qr_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }
        """)
        self.content_layout.insertWidget(1, self.qr_label)
        
        # Afficher la référence
        ref_label = QLabel(f"Référence: {reference}")
        ref_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ref_label.setAlignment(Qt.AlignCenter)
        ref_label.setStyleSheet("color: #0078d4; margin: 10px 0;")
        self.content_layout.insertWidget(2, ref_label)
        
        self._show_message(f"💡 QR Code généré - Référence: {reference}", "info")
    
    def _confirm_ussd_payment(self):
        """Confirme le paiement USSD"""
        # Dans un vrai système, on vérifierait le paiement via API
        self._show_message("✅ Paiement confirmé! Redirection vers la sélection de casier...", "success")
        
        QTimer.singleShot(2000, lambda: self.screen_changed.emit('locker', {
            'method': 'ussd',
            'amount': 5.0
        }))
    
    def _show_message(self, message: str, msg_type: str = "info"):
        """Affiche un message à l'utilisateur"""
        self.message_label.setText(message)
        
        if msg_type == "success":
            self.message_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #28a745;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }
            """)
        elif msg_type == "error":
            self.message_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #dc3545;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }
            """)
        else:  # info
            self.message_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #17a2b8;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }
            """)
        
        # Effacer le message après 5 secondes
        QTimer.singleShot(5000, lambda: self.message_label.clear())