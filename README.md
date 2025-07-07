# Système de Surveillance Réseau

Un système de surveillance réseau en temps réel utilisant Flask, SocketIO et SNMP pour monitorer l'état des équipements réseau.

## Fonctionnalités

### 🖥️ Tableau de Bord Web
- Interface web moderne et responsive
- Surveillance en temps réel via WebSocket
- Statistiques générales (appareils en ligne/hors ligne)
- Tableau de bord avec métriques détaillées

### 📊 Surveillance des Appareils
- Détection automatique de l'état (en ligne/hors ligne)
- Collecte des métriques SNMP :
  - Utilisation CPU
  - Utilisation mémoire
  - Temps de fonctionnement (uptime)
  - Trafic réseau
- Support de différents types d'appareils :
  - Routeurs
  - Commutateurs
  - Serveurs
  - Pare-feu
  - Imprimantes

### 🔔 Système de Notifications
- Alertes en temps réel dans l'interface web
- Notifications par email pour :
  - Appareils hors ligne
  - Retour en ligne des appareils
  - Utilisation CPU/mémoire élevée
  - Rapport quotidien

### 🕒 Planification Automatique
- Collecte automatique des métriques (configurable)
- Nettoyage automatique des anciennes données
- Envoi de rapports quotidiens

## Installation

### Prérequis
- Python 3.8+
- Accès SNMP aux équipements à surveiller

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd network_monitoring
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
Créer un fichier `.env` à la racine du projet :
```env
# Configuration Flask
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///network_monitoring.db

# Configuration SNMP
SNMP_COMMUNITY=public
SNMP_PORT=161
SNMP_TIMEOUT=5

# Configuration de surveillance
MONITORING_INTERVAL=30

# Configuration email (optionnel)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

5. **Démarrer l'application**
```bash
python run.py
```

L'application sera accessible sur `http://localhost:5000`

## Utilisation

### Ajouter un Appareil
1. Cliquer sur "Ajouter Appareil" dans la navigation
2. Remplir les informations :
   - Nom de l'appareil
   - Adresse IP
   - Type d'appareil
   - Communauté SNMP (par défaut : "public")
3. Cliquer sur "Ajouter"

### Surveillance en Temps Réel
- L'interface se met à jour automatiquement
- Les changements d'état sont affichés instantanément
- Les alertes apparaissent en haut de la page

### Actions sur les Appareils
- **👁️ Voir** : Afficher les détails complets de l'appareil
- **✏️ Modifier** : Éditer les paramètres de l'appareil
- **▶️ Tester** : Tester la connectivité SNMP
- **🗑️ Supprimer** : Retirer l'appareil de la surveillance

## API REST

### Endpoints disponibles

#### Appareils
- `GET /api/devices` - Liste tous les appareils
- `POST /api/devices` - Ajouter un nouvel appareil
- `GET /api/devices/{id}` - Détails d'un appareil
- `PUT /api/devices/{id}` - Modifier un appareil
- `DELETE /api/devices/{id}` - Supprimer un appareil
- `POST /api/devices/{id}/test` - Tester la connectivité

#### Métriques
- `GET /api/devices/{id}/metrics` - Récupérer les métriques d'un appareil
  - Paramètres optionnels :
    - `hours` : Nombre d'heures d'historique (défaut: 24)
    - `type` : Type de métrique (cpu, memory, etc.)

## Configuration Avancée

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Flask | `dev-secret-key...` |
| `DATABASE_URL` | URL de la base de données | `sqlite:///network_monitoring.db` |
| `SNMP_COMMUNITY` | Communauté SNMP par défaut | `public` |
| `SNMP_PORT` | Port SNMP | `161` |
| `SNMP_TIMEOUT` | Timeout SNMP (secondes) | `5` |
| `MONITORING_INTERVAL` | Intervalle de surveillance (secondes) | `30` |
| `EMAIL_ENABLED` | Activer les notifications email | `false` |
| `SMTP_SERVER` | Serveur SMTP | - |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USERNAME` | Nom d'utilisateur SMTP | - |
| `SMTP_PASSWORD` | Mot de passe SMTP | - |
| `ADMIN_EMAIL` | Email de l'administrateur | - |

### Personnalisation des Seuils d'Alerte

Les seuils d'alerte peuvent être modifiés dans `app/tasks/scheduler.py` :
- CPU élevé : 80% (par défaut)
- Mémoire élevée : 90% (par défaut)

### Base de Données

Par défaut, l'application utilise SQLite. Pour utiliser PostgreSQL ou MySQL :

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/network_monitoring

# MySQL
DATABASE_URL=mysql://user:password@localhost/network_monitoring
```

## Dépannage

### Problèmes SNMP Courants

1. **Timeout de connexion**
   - Vérifier que l'appareil est accessible
   - Vérifier la communauté SNMP
   - Vérifier que SNMP est activé sur l'appareil

2. **Communauté SNMP incorrecte**
   - Vérifier la configuration SNMP de l'appareil
   - S'assurer que la communauté est configurée

3. **Appareil non compatible**
   - Certains appareils peuvent ne pas supporter tous les OIDs
   - Les métriques peuvent être limitées

### Problèmes de Performance

- Réduire l'intervalle de surveillance pour les gros réseaux
- Nettoyer régulièrement les anciennes métriques
- Utiliser une base de données externe pour de meilleures performances

## Structure du Projet

```
network_monitoring/
├── app/
│   ├── __init__.py          # Configuration Flask
│   ├── models/
│   │   └── device.py        # Modèles de données
│   ├── routes/
│   │   ├── __init__.py
│   │   └── devices.py       # Routes API
│   ├── services/
│   │   ├── notifier.py      # Service de notifications
│   │   └── snmp.py          # Service SNMP
│   ├── sockets/
│   │   └── live_status.py   # WebSocket handlers
│   ├── static/
│   │   ├── css/
│   │   │   └── dashboard.css # Styles CSS
│   │   └── js/
│   │       └── dashboard.js  # JavaScript frontend
│   ├── tasks/
│   │   └── scheduler.py     # Tâches planifiées
│   └── templates/
│       └── dashboard.html   # Template principal
├── config.py                # Configuration
├── requirements.txt         # Dépendances Python
├── run.py                  # Point d'entrée
└── README.md               # Documentation
```

## Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation
- Vérifier les logs de l'application