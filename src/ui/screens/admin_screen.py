"""
Écran d'administration de la borne
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QTextEdit, QTabWidget,
                            QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from src.ui.screens.base_screen import BaseScreen

class AdminScreen(BaseScreen):
    """Écran d'administration pour la gestion de la borne"""

    def __init__(self, config, locker_manager, payment_manager):
        # Initialise tes attributs personnalisés en premier
        self.is_authenticated = False
        self.failed_attempts = 0
        self.max_attempts = 3
        # Ensuite seulement, appelle la classe mère
        super().__init__(config, locker_manager, payment_manager)


    def setup_ui(self):
        """Configure l'interface de l'écran d'administration"""
        super().setup_ui()
        self.title_label = self.create_title("🔧 Administration")
        self.layout.addWidget(self.title_label)
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
        self._show_login_screen()
        self.layout.addStretch()
        nav_layout = self.create_navigation_bar()
        self.layout.addLayout(nav_layout)
    
    def _show_login_screen(self):
        """Affiche l'écran de connexion administrateur"""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        login_instructions = QLabel("""
        🔐 Accès Administrateur

        Entrez le code maître pour accéder aux fonctions d'administration
        """)
        login_instructions.setFont(QFont("Segoe UI", 16))
        login_instructions.setAlignment(Qt.AlignCenter)
        login_instructions.setStyleSheet("color: #cccccc; margin: 20px 0;")
        self.content_layout.addWidget(login_instructions)
        code_layout = QHBoxLayout()
        code_label = QLabel("Code maître:")
        code_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        code_label.setStyleSheet("color: #ffffff;")
        code_layout.addWidget(code_label)
        self.master_code_input = QLineEdit()
        self.master_code_input.setFont(QFont("Segoe UI", 18))
        self.master_code_input.setPlaceholderText("Entrez le code maître...")
        self.master_code_input.setEchoMode(QLineEdit.Password)
        self.master_code_input.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        self.master_code_input.returnPressed.connect(self._authenticate)
        code_layout.addWidget(self.master_code_input)
        self.content_layout.addLayout(code_layout)
        login_button = self.create_button("🔓 Se connecter", self._authenticate)
        self.content_layout.addWidget(login_button)
        if self.failed_attempts > 0:
            attempts_label = QLabel(f"⚠️ Tentatives échouées: {self.failed_attempts}/{self.max_attempts}")
            attempts_label.setFont(QFont("Segoe UI", 12))
            attempts_label.setAlignment(Qt.AlignCenter)
            attempts_label.setStyleSheet("color: #dc3545; margin: 10px 0;")
            self.content_layout.addWidget(attempts_label)
    

    def _authenticate(self):
        """Authentifie l'administrateur"""
        entered_code = self.master_code_input.text().strip()
        master_code = self.config.get('security.master_code', '9999')
        
        if entered_code == master_code:
            self.is_authenticated = True
            self.failed_attempts = 0
            self._show_message("✅ Connexion réussie!", "success")
            QTimer.singleShot(1000, self._show_admin_panel)
        else:
            self.failed_attempts += 1
            self._show_message(f"❌ Code incorrect! ({self.failed_attempts}/{self.max_attempts})", "error")
            
            if self.failed_attempts >= self.max_attempts:
                self._show_message("🚫 Trop de tentatives échouées. Retour à l'accueil.", "error")
                QTimer.singleShot(3000, lambda: self.screen_changed.emit('home', {}))
            else:
                self.master_code_input.clear()
                self._show_login_screen()
    
    def _show_admin_panel(self):
        """Affiche le panneau d'administration principal"""
        # Nettoyer le contenu existant
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Créer les onglets d'administration
        self.admin_tabs = QTabWidget()
        self.admin_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #404040;
            }
            QTabBar::tab {
                background-color: #606060;
                color: white;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #707070;
            }
        """)
        
        # Onglet État des casiers
        self._create_lockers_tab()
        
        # Onglet Codes prépayés
        self._create_prepaid_codes_tab()
        
        # Onglet Maintenance
        self._create_maintenance_tab()
        
        # Onglet Configuration
        self._create_config_tab()
        
        self.content_layout.addWidget(self.admin_tabs)
        
        # Bouton de déconnexion
        logout_button = self.create_button("🚪 Se déconnecter", self._logout, "danger")
        self.content_layout.addWidget(logout_button)
    
    def _create_lockers_tab(self):
        """Crée l'onglet de gestion des casiers"""
        lockers_widget = QWidget()
        layout = QVBoxLayout(lockers_widget)
        
        # Titre
        title = QLabel("🔒 État des Casiers")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 15px 0;")
        layout.addWidget(title)
        
        # Tableau des casiers
        self.lockers_table = QTableWidget()
        self.lockers_table.setColumnCount(5)
        self.lockers_table.setHorizontalHeaderLabels([
            "Casier", "État", "Code Utilisateur", "Début", "Actions"
        ])
        
        # Style du tableau
        self.lockers_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Ajuster les colonnes
        header = self.lockers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.lockers_table)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        refresh_button = self.create_button("🔄 Actualiser", self._refresh_lockers_table, "secondary")
        actions_layout.addWidget(refresh_button)
        
        force_open_button = self.create_button("🔓 Ouvrir Casier", self._force_open_locker, "danger")
        actions_layout.addWidget(force_open_button)
        
        layout.addLayout(actions_layout)
        
        self.admin_tabs.addTab(lockers_widget, "🔒 Casiers")
        
        # Remplir le tableau initial
        self._refresh_lockers_table()
    
    def _create_prepaid_codes_tab(self):
        """Crée l'onglet de gestion des codes prépayés"""
        codes_widget = QWidget()
        layout = QVBoxLayout(codes_widget)
        
        # Titre
        title = QLabel("💳 Codes Prépayés")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 15px 0;")
        layout.addWidget(title)
        
        # Génération de nouveaux codes
        generation_frame = QFrame()
        generation_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        gen_layout = QHBoxLayout(generation_frame)
        
        gen_layout.addWidget(QLabel("Valeur (€):"))
        
        self.code_value_input = QLineEdit("5.00")
        self.code_value_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        gen_layout.addWidget(self.code_value_input)
        
        generate_button = self.create_button("➕ Générer Code", self._generate_prepaid_code, "primary")
        gen_layout.addWidget(generate_button)
        
        layout.addWidget(generation_frame)
        
        # Tableau des codes
        self.codes_table = QTableWidget()
        self.codes_table.setColumnCount(5)
        self.codes_table.setHorizontalHeaderLabels([
            "Code", "Valeur", "Créé", "Expiré", "Utilisé"
        ])
        
        self.codes_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        header = self.codes_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.codes_table)
        
        # Bouton d'actualisation
        refresh_codes_button = self.create_button("🔄 Actualiser", self._refresh_codes_table, "secondary")
        layout.addWidget(refresh_codes_button)
        
        self.admin_tabs.addTab(codes_widget, "💳 Codes")
        
        # Remplir le tableau initial
        self._refresh_codes_table()
    
    def _create_maintenance_tab(self):
        """Crée l'onglet de maintenance"""
        maintenance_widget = QWidget()
        layout = QVBoxLayout(maintenance_widget)
        
        # Titre
        title = QLabel("🔧 Maintenance")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 15px 0;")
        layout.addWidget(title)
        
        # Actions de maintenance
        actions_grid = QGridLayout()
        
        # Libérer tous les casiers
        free_all_button = self.create_button(
            "🔓 Libérer Tous les Casiers", 
            self._free_all_lockers, 
            "danger"
        )
        actions_grid.addWidget(free_all_button, 0, 0)
        
        # Nettoyer les codes expirés
        clean_codes_button = self.create_button(
            "🧹 Nettoyer Codes Expirés", 
            self._clean_expired_codes, 
            "secondary"
        )
        actions_grid.addWidget(clean_codes_button, 0, 1)
        
        # Redémarrer l'application
        restart_button = self.create_button(
            "🔄 Redémarrer Application", 
            self._restart_application, 
            "danger"
        )
        actions_grid.addWidget(restart_button, 1, 0)
        
        # Exporter les logs
        export_logs_button = self.create_button(
            "📄 Exporter Logs", 
            self._export_logs, 
            "secondary"
        )
        actions_grid.addWidget(export_logs_button, 1, 1)
        
        layout.addLayout(actions_grid)
        
        # Zone de logs en temps réel
        logs_label = QLabel("📋 Logs Récents:")
        logs_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logs_label.setStyleSheet("color: #ffffff; margin: 20px 0 10px 0;")
        layout.addWidget(logs_label)
        
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setMaximumHeight(200)
        self.logs_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #404040;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.logs_display)
        
        self.admin_tabs.addTab(maintenance_widget, "🔧 Maintenance")
        
        # Charger les logs récents
        self._load_recent_logs()
    
    def _create_config_tab(self):
        """Crée l'onglet de configuration"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Titre
        title = QLabel("⚙️ Configuration")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 15px 0;")
        layout.addWidget(title)
        
        # Paramètres principaux
        config_grid = QGridLayout()
        
        # Nombre de casiers
        config_grid.addWidget(QLabel("Nombre de casiers:"), 0, 0)
        self.lockers_count_input = QLineEdit(str(self.config.get('lockers.count', 8)))
        self.lockers_count_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        config_grid.addWidget(self.lockers_count_input, 0, 1)
        
        # Timeout de session
        config_grid.addWidget(QLabel("Timeout session (sec):"), 1, 0)
        self.session_timeout_input = QLineEdit(str(self.config.get('security.session_timeout', 300)))
        self.session_timeout_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        config_grid.addWidget(self.session_timeout_input, 1, 1)
        
        # Code maître
        config_grid.addWidget(QLabel("Code maître:"), 2, 0)
        self.master_code_config_input = QLineEdit(self.config.get('security.master_code', '9999'))
        self.master_code_config_input.setEchoMode(QLineEdit.Password)
        self.master_code_config_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        config_grid.addWidget(self.master_code_config_input, 2, 1)
        
        layout.addLayout(config_grid)
        
        # Bouton de sauvegarde
        save_config_button = self.create_button("💾 Sauvegarder Configuration", self._save_config)
        layout.addWidget(save_config_button)
        
        layout.addStretch()
        
        self.admin_tabs.addTab(config_widget, "⚙️ Config")
    
    def _refresh_lockers_table(self):
        """Actualise le tableau des casiers"""
        locker_count = self.config.get('lockers.count', 8)
        self.lockers_table.setRowCount(locker_count)
        
        for i in range(1, locker_count + 1):
            row = i - 1
            
            # Numéro du casier
            self.lockers_table.setItem(row, 0, QTableWidgetItem(str(i)))
            
            # État
            is_available = self.locker_manager.is_locker_available(i)
            status = "🟢 Libre" if is_available else "🔴 Occupé"
            self.lockers_table.setItem(row, 1, QTableWidgetItem(status))
            
            # Informations de session
            session = self.locker_manager.get_session_info(i)
            if session:
                self.lockers_table.setItem(row, 2, QTableWidgetItem(session.user_code))
                self.lockers_table.setItem(row, 3, QTableWidgetItem(
                    session.start_time.strftime("%H:%M:%S")
                ))
            else:
                self.lockers_table.setItem(row, 2, QTableWidgetItem("-"))
                self.lockers_table.setItem(row, 3, QTableWidgetItem("-"))
            
            # Bouton d'action
            if not is_available:
                action_button = QPushButton("🔓 Libérer")
                action_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border-radius: 4px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                action_button.clicked.connect(lambda checked, locker_id=i: self._release_locker(locker_id))
                self.lockers_table.setCellWidget(row, 4, action_button)
            else:
                self.lockers_table.setItem(row, 4, QTableWidgetItem("-"))
    
    def _refresh_codes_table(self):
        """Actualise le tableau des codes prépayés"""
        codes = list(self.payment_manager.prepaid_codes.values())
        self.codes_table.setRowCount(len(codes))
        
        for row, code in enumerate(codes):
            self.codes_table.setItem(row, 0, QTableWidgetItem(code.code))
            self.codes_table.setItem(row, 1, QTableWidgetItem(f"{code.value}€"))
            self.codes_table.setItem(row, 2, QTableWidgetItem(
                code.created_date.strftime("%d/%m/%Y %H:%M")
            ))
            
            # Vérifier si expiré
            from datetime import datetime
            is_expired = datetime.now() > code.expiry_date
            expired_text = "🔴 Oui" if is_expired else "🟢 Non"
            self.codes_table.setItem(row, 3, QTableWidgetItem(expired_text))
            
            # Vérifier si utilisé
            used_text = "🔴 Oui" if code.is_used else "🟢 Non"
            self.codes_table.setItem(row, 4, QTableWidgetItem(used_text))
    
    def _generate_prepaid_code(self):
        """Génère un nouveau code prépayé"""
        try:
            value = float(self.code_value_input.text())
            if value <= 0:
                raise ValueError("La valeur doit être positive")
            
            code = self.payment_manager.generate_prepaid_code(value)
            self._show_message(f"✅ Code généré: {code} (valeur: {value}€)", "success")
            self._refresh_codes_table()
            
        except ValueError as e:
            self._show_message(f"❌ Erreur: {e}", "error")
    
    def _force_open_locker(self):
        """Force l'ouverture d'un casier"""
        locker_id, ok = QInputDialog.getInt(
            self, 
            "Ouvrir Casier", 
            "Numéro du casier à ouvrir:",
            1, 1, self.config.get('lockers.count', 8)
        )
        
        if ok:
            master_code = self.config.get('security.master_code', '9999')
            if self.locker_manager.unlock_locker(locker_id, master_code):
                self._show_message(f"✅ Casier {locker_id} ouvert", "success")
            else:
                self._show_message(f"❌ Erreur lors de l'ouverture du casier {locker_id}", "error")
    
    def _release_locker(self, locker_id: int):
        """Libère un casier spécifique"""
        reply = QMessageBox.question(
            self, 
            "Libérer Casier", 
            f"Êtes-vous sûr de vouloir libérer le casier {locker_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.locker_manager.release_locker(locker_id):
                self._show_message(f"✅ Casier {locker_id} libéré", "success")
                self._refresh_lockers_table()
            else:
                self._show_message(f"❌ Erreur lors de la libération du casier {locker_id}", "error")
    
    def _free_all_lockers(self):
        """Libère tous les casiers"""
        reply = QMessageBox.question(
            self, 
            "Libérer Tous les Casiers", 
            "⚠️ ATTENTION: Cette action libérera TOUS les casiers occupés.\n\nÊtes-vous sûr?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            count = 0
            for locker_id in list(self.locker_manager.active_sessions.keys()):
                if self.locker_manager.release_locker(locker_id):
                    count += 1
            
            self._show_message(f"✅ {count} casiers libérés", "success")
            self._refresh_lockers_table()
    
    def _clean_expired_codes(self):
        """Nettoie les codes expirés"""
        initial_count = len(self.payment_manager.prepaid_codes)
        self.payment_manager.cleanup_expired_codes()
        final_count = len(self.payment_manager.prepaid_codes)
        
        cleaned = initial_count - final_count
        self._show_message(f"✅ {cleaned} codes expirés supprimés", "success")
        self._refresh_codes_table()
    
    def _restart_application(self):
        """Redémarre l'application"""
        reply = QMessageBox.question(
            self, 
            "Redémarrer", 
            "⚠️ L'application va redémarrer.\n\nContinuer?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import sys
            import os
            os.execl(sys.executable, sys.executable, *sys.argv)
    
    def _export_logs(self):
        """Exporte les logs"""
        from datetime import datetime
        import os
        
        try:
            log_file = f"logs/borne_{datetime.now().strftime('%Y%m%d')}.log"
            if os.path.exists(log_file):
                export_file = f"export_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                
                with open(log_file, 'r', encoding='utf-8') as src:
                    with open(export_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                self._show_message(f"✅ Logs exportés vers: {export_file}", "success")
            else:
                self._show_message("❌ Aucun fichier de log trouvé", "error")
        except Exception as e:
            self._show_message(f"❌ Erreur lors de l'export: {e}", "error")
    
    def _load_recent_logs(self):
        """Charge les logs récents"""
        from datetime import datetime
        import os
        
        try:
            log_file = f"logs/borne_{datetime.now().strftime('%Y%m%d')}.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Afficher les 20 dernières lignes
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    self.logs_display.setPlainText(''.join(recent_lines))
        except Exception as e:
            self.logs_display.setPlainText(f"Erreur lors du chargement des logs: {e}")
    
    def _save_config(self):
        """Sauvegarde la configuration"""
        try:
            # Mettre à jour la configuration
            self.config.set('lockers.count', int(self.lockers_count_input.text()))
            self.config.set('security.session_timeout', int(self.session_timeout_input.text()))
            self.config.set('security.master_code', self.master_code_config_input.text())
            
            # Sauvegarder
            self.config.save()
            
            self._show_message("✅ Configuration sauvegardée", "success")
        except Exception as e:
            self._show_message(f"❌ Erreur lors de la sauvegarde: {e}", "error")
    
    def _logout(self):
        """Déconnecte l'administrateur"""
        self.is_authenticated = False
        self.failed_attempts = 0
        self._show_message("👋 Déconnexion réussie", "info")
        QTimer.singleShot(1000, lambda: self.screen_changed.emit('home', {}))
    
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
        """Rafraîchit l'écran d'administration"""
        if self.is_authenticated and hasattr(self, 'admin_tabs'):
            current_tab = self.admin_tabs.currentIndex()
            
            if current_tab == 0:  # Onglet casiers
                self._refresh_lockers_table()
            elif current_tab == 1:  # Onglet codes
                self._refresh_codes_table()
            elif current_tab == 2:  # Onglet maintenance
                self._load_recent_logs()