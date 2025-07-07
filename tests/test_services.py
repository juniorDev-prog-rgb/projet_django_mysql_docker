import pytest
from unittest.mock import Mock, patch
from app.services.snmp import SNMPService
from app.services.notifier import NotificationService
from app.models.device import Device

class TestSNMPService:
    """Tests pour le service SNMP"""
    
    def test_ping_device_success(self):
        """Test de ping réussi"""
        snmp_service = SNMPService()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            result = snmp_service.ping_device('127.0.0.1')
            assert result is True
    
    def test_ping_device_failure(self):
        """Test de ping échoué"""
        snmp_service = SNMPService()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            result = snmp_service.ping_device('192.168.255.255')
            assert result is False
    
    def test_collect_device_metrics_no_snmp(self, app, sample_device):
        """Test de collecte de métriques sans SNMP"""
        with app.app_context():
            snmp_service = SNMPService()
            snmp_service.snmp_available = False
            
            with patch.object(snmp_service, 'ping_device', return_value=True):
                result = snmp_service.collect_device_metrics(sample_device)
                
                assert result['status'] == 'success'
                assert 'metrics' in result
                assert sample_device.status == 'online'

class TestNotificationService:
    """Tests pour le service de notifications"""
    
    def test_send_email_disabled(self, app):
        """Test d'envoi d'email désactivé"""
        with app.app_context():
            app.config['EMAIL_ENABLED'] = False
            notifier = NotificationService()
            
            result = notifier.send_email('test@example.com', 'Test', 'Body')
            assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, app):
        """Test d'envoi d'email réussi"""
        with app.app_context():
            app.config.update({
                'EMAIL_ENABLED': True,
                'SMTP_SERVER': 'smtp.test.com',
                'SMTP_USERNAME': 'test@test.com',
                'SMTP_PASSWORD': 'password'
            })
            
            mock_server = Mock()
            mock_smtp.return_value = mock_server
            
            notifier = NotificationService()
            result = notifier.send_email('test@example.com', 'Test', 'Body')
            
            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()
            mock_server.quit.assert_called_once()
