"""
Script d'installation et de configuration pour le système de surveillance réseau
Exécuter ce script pour configurer l'environnement initial
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e.stderr}")
        return False

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
    if not os.path.exists('.env'):
        print("\n📝 Création du fichier .env...")
        try:
            with open('.env.example', 'r') as example:
                content = example.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ Fichier .env créé avec succès")
            print("⚠️  Veuillez modifier le fichier .env selon vos besoins")
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier .env: {e}")
    else:
        print("✅ Fichier .env déjà existant")

def setup_database():
    """Initialise la base de données"""
    print("\n🗄️  Configuration de la base de données...")
    try:
        # Créer le répertoire pour la base de données s'il n'existe pas
        db_dir = os.path.dirname('network_monitoring.db')
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Test de connexion à la base de données
        conn = sqlite3.connect('network_monitoring.db')
        conn.close()
        print("✅ Base de données configurée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de la base de données: {e}")
        return False

def add_sample_devices():
    """Ajoute des appareils d'exemple pour tester"""
    print("\n🖥️  Ajout d'appareils d'exemple...")
    try:
        conn = sqlite3.connect('network_monitoring.db')
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'")
        if not cursor.fetchone():
            print("⚠️  Les tables n'existent pas encore. Elles seront créées au premier démarrage.")
            conn.close()
            return True
        
        # Vérifier s'il y a déjà des appareils
        cursor.execute("SELECT COUNT(*) FROM devices")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_devices = [
                ('Routeur Principal', '192.168.1.1', 'router', 'public'),
                ('Switch Bureau', '192.168.1.10', 'switch', 'public'),
                ('Serveur Web', '192.168.1.100', 'server', 'public'),
            ]
            
            for name, ip, device_type, community in sample_devices:
                cursor.execute("""
                    INSERT INTO devices (name, ip_address, device_type, snmp_community, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'unknown', ?, ?)
                """, (name, ip, device_type, community, datetime.utcnow(), datetime.utcnow()))
            
            conn.commit()
            print(f"✅ {len(sample_devices)} appareils d'exemple ajoutés")
        else:
            print(f"ℹ️  {count} appareils déjà présents dans la base de données")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des appareils d'exemple: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("🚀 Installation du Système de Surveillance Réseau")
    print("=" * 50)
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Créer l'environnement virtuel
    if not os.path.exists('venv'):
        success = run_command(f"{sys.executable} -m venv venv", "Création de l'environnement virtuel")
        if not success:
            print("❌ Échec de la création de l'environnement virtuel")
            sys.exit(1)
    else:
        print("✅ Environnement virtuel déjà existant")
    
    # Déterminer la commande d'activation selon l'OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Installer les dépendances
    success = run_command(f"{pip_cmd} install -r requirements.txt", "Installation des dépendances")
    if not success:
        print("❌ Échec de l'installation des dépendances")
        sys.exit(1)
    
    # Créer le fichier .env
    create_env_file()
    
    # Configurer la base de données
    setup_database()
    
    print("\n" + "=" * 50)
    print("🎉 Installation terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Modifier le fichier .env selon vos besoins")
    print("2. Activer l'environnement virtuel:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Démarrer l'application:")
    print("   python run.py")
    print("4. Ouvrir http://localhost:5000 dans votre navigateur")
    print("\n📖 Consultez le README.md pour plus d'informations")

if __name__ == "__main__":
    main()
