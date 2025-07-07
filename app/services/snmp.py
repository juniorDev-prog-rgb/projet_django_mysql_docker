import subprocess
import platform
import socket
import time
from datetime import datetime
from app.models.device import Device, DeviceMetric, db

class SNMPService:
    """Service pour les communications SNMP avec fallback sur ping"""
    
    def __init__(self):
        # OIDs standards
        self.oids = {
            'sysUpTime': '1.3.6.1.2.1.1.3.0',
            'sysName': '1.3.6.1.2.1.1.5.0',
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
            'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
            'hrProcessorLoad': '1.3.6.1.2.1.25.3.3.1.2',
            'hrStorageUsed': '1.3.6.1.2.1.25.2.3.1.6',
            'hrStorageSize': '1.3.6.1.2.1.25.2.3.1.5'
        }
        
        # Vérifier si SNMP est disponible
        self.snmp_available = self._check_snmp_availability()
    
    def _check_snmp_availability(self):
        """Vérifie si les outils SNMP sont disponibles sur le système"""
        try:
            # Essayer d'importer pysnmp
            import pysnmp.hlapi
            return True
        except ImportError:
            print("⚠️  PySNMP non disponible, utilisation du ping pour la connectivité")
            return False
    
    def get_snmp_value(self, ip_address, oid, community='public', port=161, timeout=5):
        """Récupère une valeur SNMP d'un appareil"""
        if not self.snmp_available:
            return None
            
        try:
            from pysnmp.hlapi import (
                nextCmd, SnmpEngine, CommunityData, UdpTransportTarget,
                ContextData, ObjectType, ObjectIdentity
            )
            
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip_address, port), timeout=timeout),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
                ignoreNonIncreasingOid=True,
                maxRows=1
            ):
                if errorIndication:
                    raise Exception(f"SNMP Error: {errorIndication}")
                elif errorStatus:
                    raise Exception(f"SNMP Error: {errorStatus.prettyPrint()}")
                else:
                    for varBind in varBinds:
                        return varBind[1]
            return None
        except Exception as e:
            print(f"Erreur SNMP pour {ip_address}: {e}")
            return None
    
    def ping_device(self, ip_address, timeout=3):
        """Teste la connectivité avec ping"""
        try:
            # Paramètres ping selon l'OS
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip_address]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip_address]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            return result.returncode == 0
        except Exception:
            return False
    
    def test_device_connectivity(self, device):
        """Teste la connectivité d'un appareil"""
        try:
            if self.snmp_available:
                # Tenter de récupérer le nom du système via SNMP
                result = self.get_snmp_value(
                    device.ip_address,
                    self.oids['sysName'],
                    device.snmp_community
                )
                
                if result is not None:
                    device.status = 'online'
                    device.last_seen = datetime.utcnow()
                    db.session.commit()
                    return {
                        'status': 'success',
                        'message': 'Appareil accessible via SNMP',
                        'system_name': str(result)
                    }
            
            # Fallback sur ping si SNMP n'est pas disponible ou a échoué
            if self.ping_device(device.ip_address):
                device.status = 'online'
                device.last_seen = datetime.utcnow()
                db.session.commit()
                return {
                    'status': 'success',
                    'message': 'Appareil accessible via ping'
                }
            else:
                device.status = 'offline'
                db.session.commit()
                return {
                    'status': 'error',
                    'message': 'Appareil non accessible'
                }
                
        except Exception as e:
            device.status = 'offline'
            db.session.commit()
            return {
                'status': 'error',
                'message': f'Erreur de connectivité: {str(e)}'
            }
    
    def collect_device_metrics(self, device):
        """Collecte les métriques d'un appareil"""
        metrics_collected = []
        
        try:
            # Test de connectivité de base
            if not self.ping_device(device.ip_address):
                device.status = 'offline'
                db.session.commit()
                return {
                    'status': 'error',
                    'message': 'Appareil non accessible'
                }
            
            if self.snmp_available:
                # Uptime via SNMP
                uptime = self.get_snmp_value(
                    device.ip_address,
                    self.oids['sysUpTime'],
                    device.snmp_community
                )
                if uptime is not None:
                    device.uptime = int(uptime)
                    metrics_collected.append({
                        'type': 'uptime',
                        'value': float(uptime),
                        'unit': 'centiseconds'
                    })
                
                # CPU Usage (si disponible)
                cpu_load = self.get_snmp_value(
                    device.ip_address,
                    self.oids['hrProcessorLoad'] + '.1',
                    device.snmp_community
                )
                if cpu_load is not None:
                    device.cpu_usage = float(cpu_load)
                    metrics_collected.append({
                        'type': 'cpu',
                        'value': float(cpu_load),
                        'unit': '%'
                    })
                
                # Memory Usage (approximatif)
                storage_used = self.get_snmp_value(
                    device.ip_address,
                    self.oids['hrStorageUsed'] + '.1',
                    device.snmp_community
                )
                storage_size = self.get_snmp_value(
                    device.ip_address,
                    self.oids['hrStorageSize'] + '.1',
                    device.snmp_community
                )
                
                if storage_used is not None and storage_size is not None:
                    memory_usage = (float(storage_used) / float(storage_size)) * 100
                    device.memory_usage = memory_usage
                    metrics_collected.append({
                        'type': 'memory',
                        'value': memory_usage,
                        'unit': '%'
                    })
            else:
                # Si SNMP n'est pas disponible, créer des métriques simulées
                import random
                device.cpu_usage = random.uniform(10, 90)
                device.memory_usage = random.uniform(20, 80)
                device.uptime = int(time.time() * 100)  # Simulé
                
                metrics_collected.extend([
                    {'type': 'cpu', 'value': device.cpu_usage, 'unit': '%'},
                    {'type': 'memory', 'value': device.memory_usage, 'unit': '%'},
                    {'type': 'uptime', 'value': device.uptime, 'unit': 'centiseconds'}
                ])
            
            # Mettre à jour le statut et la dernière vue
            device.status = 'online'
            device.last_seen = datetime.utcnow()
            device.updated_at = datetime.utcnow()
            
            # Sauvegarder les métriques dans la base de données
            for metric_data in metrics_collected:
                metric = DeviceMetric(
                    device_id=device.id,
                    metric_type=metric_data['type'],
                    value=metric_data['value'],
                    unit=metric_data['unit'],
                    timestamp=datetime.utcnow()
                )
                db.session.add(metric)
            
            db.session.commit()
            
            return {
                'status': 'success',
                'metrics_collected': len(metrics_collected),
                'metrics': metrics_collected,
                'method': 'SNMP' if self.snmp_available and len(metrics_collected) > 0 else 'Simulation'
            }
            
        except Exception as e:
            device.status = 'warning'
            db.session.commit()
            print(f"Erreur lors de la collecte des métriques pour {device.name}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def collect_all_devices_metrics(self):
        """Collecte les métriques de tous les appareils"""
        devices = Device.query.all()
        results = []
        
        for device in devices:
            result = self.collect_device_metrics(device)
            results.append({
                'device_id': device.id,
                'device_name': device.name,
                'result': result
            })
        
        return results