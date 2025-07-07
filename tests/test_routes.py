import pytest
import json
from app.models.device import Device, db

class TestDeviceRoutes:
    """Tests pour les routes des appareils"""
    
    def test_dashboard_page(self, client):
        """Test de la page d'accueil"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Surveillance R\xc3\xa9seau' in response.data
    
    def test_get_devices_empty(self, client):
        """Test de récupération des appareils (liste vide)"""
        response = client.get('/api/devices')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_add_device_success(self, client, app):
        """Test d'ajout d'appareil réussi"""
        device_data = {
            'name': 'Test Router',
            'ip_address': '192.168.1.1',
            'device_type': 'router',
            'snmp_community': 'public'
        }
        
        response = client.post('/api/devices', 
                             data=json.dumps(device_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Router'
        assert data['ip_address'] == '192.168.1.1'
        
        # Vérifier que l'appareil est en base
        with app.app_context():
            device = Device.query.filter_by(ip_address='192.168.1.1').first()
            assert device is not None
            assert device.name == 'Test Router'
    
    def test_add_device_invalid_ip(self, client):
        """Test d'ajout d'appareil avec IP invalide"""
        device_data = {
            'name': 'Test Device',
            'ip_address': 'invalid-ip',
            'device_type': 'server'
        }
        
        response = client.post('/api/devices',
                             data=json.dumps(device_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Adresse IP invalide' in data['error']
    
    def test_add_device_missing_fields(self, client):
        """Test d'ajout d'appareil avec champs manquants"""
        device_data = {
            'name': 'Test Device'
            # ip_address et device_type manquants
        }
        
        response = client.post('/api/devices',
                             data=json.dumps(device_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_device_by_id(self, client, app, sample_device):
        """Test de récupération d'appareil par ID"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            device_id = sample_device.id
        
        response = client.get(f'/api/devices/{device_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Router'
    
    def test_get_device_not_found(self, client):
        """Test de récupération d'appareil inexistant"""
        response = client.get('/api/devices/999')
        assert response.status_code == 404
    
    def test_delete_device(self, client, app, sample_device):
        """Test de suppression d'appareil"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            device_id = sample_device.id
        
        response = client.delete(f'/api/devices/{device_id}')
        assert response.status_code == 200
        
        # Vérifier que l'appareil est supprimé
        with app.app_context():
            device = Device.query.get(device_id)
            assert device is None
