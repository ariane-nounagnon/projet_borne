# 🔋 Borne de Recharge - Application de Gestion

Une application complète de gestion de borne de recharge pour smartphones et appareils électroniques, développée en Python avec PyQt5.

## 🎯 Fonctionnalités

### 🔐 Méthodes d'Accès et de Paiement
- **Code Prépayé**: Codes à usage unique achetés en boutique
- **Digicode Personnel**: Code à 4 chiffres choisi par l'utilisateur
- **Paiement QR**: Génération de QR codes pour paiement à distance
- **Paiement USSD**: Compatible avec tous les téléphones

### 🔒 Gestion des Casiers
- 8 casiers sécurisés par défaut (configurable)
- Verrouillage automatique après fermeture
- Code maître de secours pour les techniciens
- Gestion des sessions avec timeout automatique

### 🛠️ Administration
- Interface d'administration complète
- Gestion des codes prépayés
- Monitoring des casiers en temps réel
- Maintenance et configuration système
- Export des logs d'activité

### 🌍 Interface Utilisateur
- Interface tactile optimisée
- Design moderne et ergonomique
- Multilingue (français par défaut)
- Mode plein écran pour bornes

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- PyQt5
- Modules Python additionnels (voir requirements.txt)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancement de l'application
```bash
python main.py
```

## 📁 Structure du Projet

```
projet_borne/
├── main.py                    # Point d'entrée principal
├── config.json               # Configuration de l'application
├── requirements.txt           # Dépendances Python
├── src/
│   ├── core/                 # Logique métier
│   │   ├── config.py         # Gestionnaire de configuration
│   │   ├── logger.py         # Système de logging
│   │   ├── locker_manager.py # Gestion des casiers
│   │   └── payment_manager.py # Gestion des paiements
│   └── ui/                   # Interface utilisateur
│       ├── main_window.py    # Fenêtre principale
│       └── screens/          # Écrans de l'application
│           ├── base_screen.py    # Écran de base
│           ├── home_screen.py    # Écran d'accueil
│           ├── payment_screen.py # Écran de paiement
│           ├── locker_screen.py  # Écran des casiers
│           └── admin_screen.py   # Écran d'administration
├── data/                     # Données de l'application
│   ├── sessions.json         # Sessions actives
│   ├── lockers.json          # État des casiers
│   └── prepaid_codes.json    # Codes prépayés
└── logs/                     # Fichiers de logs
```

## ⚙️ Configuration

Le fichier `config.json` permet de personnaliser:
- Nombre de casiers
- Codes de sécurité
- Timeouts de session
- URLs de paiement
- Paramètres d'affichage

## 🔧 Administration

### Accès Administrateur
- Code par défaut: `9999`
- Fonctionnalités:
  - Gestion des casiers
  - Génération de codes prépayés
  - Maintenance système
  - Configuration avancée

### Codes Prépayés
- Génération automatique de codes uniques
- Gestion des dates d'expiration
- Suivi des utilisations

## 🔒 Sécurité

- Codes maître pour accès technique
- Chiffrement des données sensibles
- Logs d'audit complets
- Timeouts de sécurité
- Limitation des tentatives d'accès

## 🌱 Écologie

- Optimisé pour alimentation solaire
- Gestion intelligente de l'énergie
- Interface éco-responsable

## 📱 Compatibilité

- Raspberry Pi 4 (recommandé)
- Écrans tactiles
- Claviers physiques
- Systèmes Linux/Windows

## 🛠️ Développement

### Architecture
- **Modèle MVC**: Séparation claire entre logique et interface
- **Modularité**: Composants indépendants et réutilisables
- **Extensibilité**: Facilité d'ajout de nouvelles fonctionnalités

### Technologies
- **Python 3.8+**: Langage principal
- **PyQt5**: Framework d'interface graphique
- **JSON**: Stockage des données
- **QR Code**: Génération de codes QR
- **Cryptography**: Sécurisation des données

## 📄 Licence

Ce projet est développé pour un usage commercial de borne de recharge.

## 🤝 Support

Pour toute question ou support technique, consultez les logs de l'application ou contactez l'équipe de développement.

---

**🔋 Borne de Recharge** - Solution complète pour la recharge sécurisée d'appareils électroniques