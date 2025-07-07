import pytest
import tempfile
import os
from app import create_app, db
from app.models.device import Device

@pytest.fixture
def app():
    """Crée une instance d'application pour les tests"""
    # Créer un fichier de base de données temporaire
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuration de test
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'MONITORING_INTERVAL': 60,
        'EMAIL_ENABLED': False
    }
    
    # Créer l'application avec la configuration de test
    app = create_app()
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        
        # Nettoyage
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Client de test Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de commandes CLI pour les tests"""
    return app.test_cli_runner()

@pytest.fixture
def sample_device():
    """Appareil de test"""
    return Device(
        name="Test Router",
        ip_address="192.168.1.1",
        device_type="router",
        snmp_community="public"
    )
