"""
Écran de gestion des casiers
"""

import secrets
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.ui.screens.base_screen import BaseScreen

class LockerScreen(BaseScreen):
    """Écran de sélection et gestion des casiers"""
    
    def __init__(self, config, locker_manager, payment_manager):
        super().__init__(config, locker_manager, payment_manager)
        self.access_method = 'digicode'
        self.access_data = {}
        self.selected_locker = None
    
    def setup_ui(self):
        """Configure l'interface de l'écran des casiers"""
        super().setup_ui()
        
        # Titre
        self.title_label = self.create_title("🔒 Sélection de Casier")
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
        """Configure l'écran selon la méthode d'accès"""
        self.access_data = data
        self.access_method = data.get('method', 'digicode')
        
        # Nettoyer le contenu existant
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Configurer selon la méthode
        if self.access_method == 'digicode':
            self._setup_digicode_selection()
        else:
            self._setup_locker_selection()
    
    def _setup_digicode_selection(self):
        """Configure l'interface pour la sélection avec digicode"""
        self.title_label.setText("🔢 Accès par Digicode Personnel")
        
        # Instructions
        instructions = QLabel("""
        🔐 Choisissez votre code personnel à 4 chiffres
        
        Ce code vous permettra de récupérer votre appareil
        Mémorisez-le bien, il sera nécessaire pour ouvrir le casier
        """)
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(instructions)
        
        # Sélection du code
        code_layout = QHBoxLayout()
        
        code_label = QLabel("Votre code (4 chiffres):")
        code_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        code_label.setStyleSheet("color: #ffffff;")
        code_layout.addWidget(code_label)
        
        self.digicode_input = QLineEdit()
        self.digicode_input.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.digicode_input.setPlaceholderText("0000")
        self.digicode_input.setMaxLength(4)
        self.digicode_input.setEchoMode(QLineEdit.Password)
        self.digicode_input.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 8px;
                padding: 15px;
                color: #ffffff;
                text-align: center;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        self.digicode_input.textChanged.connect(self._on_digicode_changed)
        code_layout.addWidget(self.digicode_input)
        
        self.content_layout.addLayout(code_layout)
        
        # Bouton de génération automatique
        generate_button = self.create_button(
            "🎲 Générer un code aléatoirement", 
            self._generate_random_code,
            "secondary"
        )
        self.content_layout.addWidget(generate_button)
        
        # Clavier numérique
        self._create_numeric_keyboard()
        
        # Bouton de validation
        self.validate_digicode_button = self.create_button(
            "✅ Confirmer et choisir un casier", 
            self._confirm_digicode
        )
        self.validate_digicode_button.setEnabled(False)
        self.content_layout.addWidget(self.validate_digicode_button)
    
    def _setup_locker_selection(self):
        """Configure l'interface pour la sélection de casier"""
        method_names = {
            'prepaid': 'Code Prépayé',
            'qr': 'QR Code',
            'ussd': 'USSD'
        }
        
        method_name = method_names.get(self.access_method, 'Paiement')
        self.title_label.setText(f"🔒 Sélection de Casier - {method_name}")
        
        # Instructions
        instructions = QLabel("""
        📦 Choisissez un casier libre pour votre appareil
        
        Cliquez sur un casier vert pour le sélectionner
        Les casiers rouges sont déjà occupés
        """)
        instructions.setFont(QFont("Segoe UI", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(instructions)
        
        # Grille des casiers
        self._create_locker_grid()
        
        # Informations sur le casier sélectionné
        self.selection_info = QLabel("Aucun casier sélectionné")
        self.selection_info.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.selection_info.setAlignment(Qt.AlignCenter)
        self.selection_info.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
        """)
        self.content_layout.addWidget(self.selection_info)
        
        # Bouton de confirmation
        self.confirm_selection_button = self.create_button(
            "✅ Réserver ce casier", 
            self._confirm_locker_selection
        )
        self.confirm_selection_button.setEnabled(False)
        self.content_layout.addWidget(self.confirm_selection_button)
    
    def _create_numeric_keyboard(self):
        """Crée un clavier numérique pour la saisie tactile"""
        keyboard_frame = QFrame()
        keyboard_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 8px;
                margin: 20px 0;
            }
        """)
        
        keyboard_layout = QGridLayout(keyboard_frame)
        
        # Touches du clavier numérique
        keys = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['⌫', '0', '✅']
        ]
        
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                button = QPushButton(key)
                button.setFont(QFont("Segoe UI", 18, QFont.Bold))
                button.setMinimumSize(80, 60)
                
                if key == '⌫':
                    button.clicked.connect(self._backspace_digicode)
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #d13438;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #b52d32;
                        }
                    """)
                elif key == '✅':
                    button.clicked.connect(self._confirm_digicode)
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #28a745;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                        }
                    """)
                else:
                    button.clicked.connect(lambda checked, k=key: self._add_digit(k))
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #606060;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #707070;
                        }
                    """)
                
                keyboard_layout.addWidget(button, row, col)
        
        self.content_layout.addWidget(keyboard_frame)
    
    def _create_locker_grid(self):
        """Crée la grille des casiers sélectionnables"""
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
        """)
        
        grid_layout = QGridLayout(grid_frame)
        
        locker_count = self.config.get('lockers.count', 8)
        cols = 4
        
        self.locker_buttons = {}
        
        for i in range(1, locker_count + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            
            is_available = self.locker_manager.is_locker_available(i)
            
            button = QPushButton(f"Casier {i}")
            button.setFont(QFont("Segoe UI", 14, QFont.Bold))
            button.setMinimumSize(120, 100)
            
            if is_available:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border-radius: 12px;
                        border: 3px solid #20c997;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                        border-color: #17a2b8;
                    }
                    QPushButton:pressed {
                        background-color: #1e7e34;
                    }
                """)
                button.setText(f"🟢\nCasier {i}\nLIBRE")
                button.clicked.connect(lambda checked, locker_id=i: self._select_locker(locker_id))
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border-radius: 12px;
                        border: 3px solid #c82333;
                    }
                """)
                button.setText(f"🔴\nCasier {i}\nOCCUPÉ")
                button.setEnabled(False)
            
            self.locker_buttons[i] = button
            grid_layout.addWidget(button, row, col)
        
        self.content_layout.addWidget(grid_frame)
    
    def _add_digit(self, digit: str):
        """Ajoute un chiffre au digicode"""
        current_text = self.digicode_input.text()
        if len(current_text) < 4:
            self.digicode_input.setText(current_text + digit)
    
    def _backspace_digicode(self):
        """Supprime le dernier chiffre du digicode"""
        current_text = self.digicode_input.text()
        self.digicode_input.setText(current_text[:-1])
    
    def _generate_random_code(self):
        """Génère un code aléatoire à 4 chiffres"""
        random_code = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        self.digicode_input.setText(random_code)
        
        # Afficher le code temporairement
        self.digicode_input.setEchoMode(QLineEdit.Normal)
        QTimer.singleShot(3000, lambda: self.digicode_input.setEchoMode(QLineEdit.Password))
        
        self._show_message(f"💡 Code généré: {random_code} (mémorisez-le!)", "info")
    
    def _on_digicode_changed(self, text: str):
        """Gère le changement de texte dans le champ digicode"""
        # Activer/désactiver le bouton de validation
        self.validate_digicode_button.setEnabled(len(text) == 4)
    
    def _confirm_digicode(self):
        """Confirme le digicode et passe à la sélection de casier"""
        code = self.digicode_input.text().strip()
        
        if len(code) != 4:
            self._show_message("❌ Le code doit contenir exactement 4 chiffres", "error")
            return
        
        if not code.isdigit():
            self._show_message("❌ Le code ne doit contenir que des chiffres", "error")
            return
        
        # Sauvegarder le code et passer à la sélection de casier
        self.access_data['user_code'] = code
        self._show_message(f"✅ Code confirmé! Choisissez maintenant un casier", "success")
        
        # Changer l'interface pour la sélection de casier
        QTimer.singleShot(1500, self._switch_to_locker_selection)
    
    def _switch_to_locker_selection(self):
        """Passe à l'interface de sélection de casier"""
        # Nettoyer le contenu existant
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Configurer l'interface de sélection
        self._setup_locker_selection()
    
    def _select_locker(self, locker_id: int):
        """Sélectionne un casier"""
        # Réinitialiser tous les boutons
        for lid, button in self.locker_buttons.items():
            if self.locker_manager.is_locker_available(lid):
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border-radius: 12px;
                        border: 3px solid #20c997;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                        border-color: #17a2b8;
                    }
                """)
        
        # Mettre en surbrillance le casier sélectionné
        selected_button = self.locker_buttons[locker_id]
        selected_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 12px;
                border: 3px solid #17a2b8;
            }
        """)
        
        self.selected_locker = locker_id
        self.selection_info.setText(f"🎯 Casier {locker_id} sélectionné")
        self.selection_info.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #0078d4;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
        """)
        
        self.confirm_selection_button.setEnabled(True)
        
        self._show_message(f"✅ Casier {locker_id} sélectionné", "success")
    
    def _confirm_locker_selection(self):
        """Confirme la sélection du casier et effectue la réservation"""
        if not self.selected_locker:
            self._show_message("❌ Veuillez sélectionner un casier", "error")
            return
        
        # Générer un code utilisateur si nécessaire
        if self.access_method == 'digicode':
            user_code = self.access_data.get('user_code', '0000')
        else:
            # Générer un code aléatoire pour les autres méthodes
            user_code = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        
        # Réserver le casier
        payment_method = self.access_method
        amount = self.access_data.get('amount', 0.0)
        
        success = self.locker_manager.reserve_locker(
            self.selected_locker, 
            user_code, 
            payment_method, 
            amount
        )
        
        if success:
            self._show_success_dialog(user_code)
        else:
            self._show_message("❌ Erreur lors de la réservation du casier", "error")
    
    def _show_success_dialog(self, user_code: str):
        """Affiche le dialogue de succès avec les informations importantes"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎉 Réservation Confirmée")
        dialog.setModal(True)
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Titre de succès
        success_title = QLabel("🎉 Casier Réservé avec Succès!")
        success_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        success_title.setAlignment(Qt.AlignCenter)
        success_title.setStyleSheet("""
            QLabel {
                color: #28a745;
                margin: 20px 0;
                padding: 20px;
                background-color: #404040;
                border-radius: 12px;
            }
        """)
        layout.addWidget(success_title)
        
        # Informations importantes
        info_text = f"""
        📦 Casier: {self.selected_locker}
        🔐 Votre code: {user_code}
        💳 Méthode: {self.access_method.title()}
        
        ⚠️ IMPORTANT:
        • Mémorisez bien votre code: {user_code}
        • Ce code est nécessaire pour récupérer votre appareil
        • Placez votre appareil dans le casier et fermez-le
        • Le casier se verrouillera automatiquement
        
        🔋 Bonne recharge!
        """
        
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Segoe UI", 14))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #404040;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
                line-height: 1.6;
            }
        """)
        layout.addWidget(info_label)
        
        # Boutons
        button_box = QDialogButtonBox()
        
        ok_button = QPushButton("✅ J'ai noté mon code")
        ok_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        
        button_box.addButton(ok_button, QDialogButtonBox.AcceptRole)
        layout.addWidget(button_box)
        
        # Afficher le dialogue
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Retourner à l'écran d'accueil
            QTimer.singleShot(500, lambda: self.screen_changed.emit('home', {}))
    
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
    
    def refresh(self):
        """Rafraîchit l'écran des casiers"""
        if hasattr(self, 'locker_buttons'):
            # Mettre à jour l'état des boutons de casiers
            for locker_id, button in self.locker_buttons.items():
                is_available = self.locker_manager.is_locker_available(locker_id)
                
                if is_available:
                    button.setEnabled(True)
                    button.setText(f"🟢\nCasier {locker_id}\nLIBRE")
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #28a745;
                            color: white;
                            border-radius: 12px;
                            border: 3px solid #20c997;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                            border-color: #17a2b8;
                        }
                    """)
                else:
                    button.setEnabled(False)
                    button.setText(f"🔴\nCasier {locker_id}\nOCCUPÉ")
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #dc3545;
                            color: white;
                            border-radius: 12px;
                            border: 3px solid #c82333;
                        }
                    """)