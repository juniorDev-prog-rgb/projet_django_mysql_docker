import pytest
from datetime import datetime
from app.models.device import Device, DeviceMetric, db

class TestDevice:
    """Tests pour le modèle Device"""
    
    def test_device_creation(self, app):
        """Test de création d'un appareil"""
        with app.app_context():
            device = Device(
                name="Test Device",
                ip_address="192.168.1.100",
                device_type="server"
            )
            db.session.add(device)
            db.session.commit()
            
            assert device.id is not None
            assert device.name == "Test Device"
            assert device.ip_address == "192.168.1.100"
            assert device.device_type == "server"
            assert device.status == "unknown"
            assert device.snmp_community == "public"
    
    def test_device_to_dict(self, app, sample_device):
        """Test de sérialisation d'un appareil"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            
            device_dict = sample_device.to_dict()
            
            assert device_dict['name'] == "Test Router"
            assert device_dict['ip_address'] == "192.168.1.1"
            assert device_dict['device_type'] == "router"
            assert 'id' in device_dict
            assert 'created_at' in device_dict
    
    def test_device_metrics_relationship(self, app, sample_device):
        """Test de la relation avec les métriques"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            
            # Ajouter une métrique
            metric = DeviceMetric(
                device_id=sample_device.id,
                metric_type="cpu",
                value=50.0,
                unit="%"
            )
            db.session.add(metric)
            db.session.commit()
            
            assert len(sample_device.metrics) == 1
            assert sample_device.metrics[0].metric_type == "cpu"
            assert sample_device.metrics[0].value == 50.0

class TestDeviceMetric:
    """Tests pour le modèle DeviceMetric"""
    
    def test_metric_creation(self, app, sample_device):
        """Test de création d'une métrique"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            
            metric = DeviceMetric(
                device_id=sample_device.id,
                metric_type="memory",
                value=75.5,
                unit="%"
            )
            db.session.add(metric)
            db.session.commit()
            
            assert metric.id is not None
            assert metric.device_id == sample_device.id
            assert metric.metric_type == "memory"
            assert metric.value == 75.5
            assert metric.unit == "%"
    
    def test_metric_to_dict(self, app, sample_device):
        """Test de sérialisation d'une métrique"""
        with app.app_context():
            db.session.add(sample_device)
            db.session.commit()
            
            metric = DeviceMetric(
                device_id=sample_device.id,
                metric_type="bandwidth",
                value=100.0,
                unit="Mbps"
            )
            db.session.add(metric)
            db.session.commit()
            
            metric_dict = metric.to_dict()
            
            assert metric_dict['device_id'] == sample_device.id
            assert metric_dict['metric_type'] == "bandwidth"
            assert metric_dict['value'] == 100.0
            assert metric_dict['unit'] == "Mbps"
            assert 'timestamp' in metric_dict
