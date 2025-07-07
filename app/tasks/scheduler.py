from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.snmp import SNMPService
from app.services.notifier import NotificationService
from app.models.device import Device
from app.sockets.live_status import broadcast_device_update, broadcast_devices_stats, broadcast_alert
from datetime import datetime, timedelta
import atexit
import logging

class MonitoringScheduler:
    """Planificateur pour les tâches de surveillance automatique"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.app = app
        self.snmp_service = SNMPService()
        self.notification_service = NotificationService()
        self.logger = logging.getLogger(__name__)
        
        # Garder trace des états précédents pour détecter les changements
        self.previous_device_states = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialise le planificateur avec l'application Flask"""
        self.app = app
        
        with app.app_context():
            self.scheduler = BackgroundScheduler()
            
            # Planifier la collecte des métriques
            monitoring_interval = app.config.get('MONITORING_INTERVAL', 30)
            self.scheduler.add_job(
                func=self.collect_all_metrics,
                trigger=IntervalTrigger(seconds=monitoring_interval),
                id='collect_metrics',
                name='Collecte des métriques',
                replace_existing=True
            )
            
            # Planifier le nettoyage des anciennes métriques (tous les jours à 2h)
            self.scheduler.add_job(
                func=self.cleanup_old_metrics,
                trigger='cron',
                hour=2,
                minute=0,
                id='cleanup_metrics',
                name='Nettoyage des métriques',
                replace_existing=True
            )
            
            # Planifier l'envoi du rapport quotidien (tous les jours à 8h)
            self.scheduler.add_job(
                func=self.send_daily_report,
                trigger='cron',
                hour=8,
                minute=0,
                id='daily_report',
                name='Rapport quotidien',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.logger.info("Planificateur de surveillance démarré")
            
            # Arrêter le planificateur à la fermeture de l'application
            atexit.register(lambda: self.scheduler.shutdown())
    
    def collect_all_metrics(self):
        """Collecte les métriques de tous les appareils"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                devices = Device.query.all()
                online_count = 0
                offline_count = 0
                warning_count = 0
                
                for device in devices:
                    previous_status = self.previous_device_states.get(device.id)
                    
                    # Collecter les métriques
                    result = self.snmp_service.collect_device_metrics(device)
                    
                    # Vérifier les changements d'état
                    current_status = device.status
                    
                    if previous_status and previous_status != current_status:
                        self._handle_status_change(device, previous_status, current_status)
                    
                    # Vérifier les seuils d'alerte
                    self._check_alert_thresholds(device)
                    
                    # Compter les statuts
                    if current_status == 'online':
                        online_count += 1
                    elif current_status == 'offline':
                        offline_count += 1
                    elif current_status == 'warning':
                        warning_count += 1
                    
                    # Mettre à jour l'état précédent
                    self.previous_device_states[device.id] = current_status
                    
                    # Diffuser la mise à jour en temps réel
                    broadcast_device_update(device)
                
                # Diffuser les statistiques mises à jour
                stats = {
                    'total': len(devices),
                    'online': online_count,
                    'offline': offline_count,
                    'warning': warning_count
                }
                broadcast_devices_stats(stats)
                
                self.logger.info(f"Métriques collectées pour {len(devices)} appareils")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la collecte des métriques: {e}")
    
    def _handle_status_change(self, device, previous_status, current_status):
        """Gère les changements d'état d'un appareil"""
        if previous_status == 'offline' and current_status == 'online':
            # Appareil de nouveau en ligne
            self.notification_service.notify_device_up(device)
            broadcast_alert('info', f"L'appareil {device.name} est de nouveau en ligne", device)
            
        elif previous_status == 'online' and current_status == 'offline':
            # Appareil hors ligne
            self.notification_service.notify_device_down(device)
            broadcast_alert('error', f"L'appareil {device.name} est hors ligne", device)
    
    def _check_alert_thresholds(self, device):
        """Vérifie les seuils d'alerte pour un appareil"""
        # Seuil CPU élevé (80%)
        if device.cpu_usage and device.cpu_usage > 80:
            self.notification_service.notify_high_cpu_usage(device, device.cpu_usage)
            broadcast_alert('warning', f"Utilisation CPU élevée sur {device.name}: {device.cpu_usage}%", device)
        
        # Seuil mémoire élevé (90%)
        if device.memory_usage and device.memory_usage > 90:
            self.notification_service.notify_high_memory_usage(device, device.memory_usage)
            broadcast_alert('warning', f"Utilisation mémoire élevée sur {device.name}: {device.memory_usage}%", device)
    
    def cleanup_old_metrics(self):
        """Nettoie les anciennes métriques (garde 30 jours)"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                from app.models.device import DeviceMetric, db
                
                # Supprimer les métriques de plus de 30 jours
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                old_metrics = DeviceMetric.query.filter(DeviceMetric.timestamp < cutoff_date).all()
                
                for metric in old_metrics:
                    db.session.delete(metric)
                
                db.session.commit()
                self.logger.info(f"Nettoyage terminé: {len(old_metrics)} anciennes métriques supprimées")
                
            except Exception as e:
                self.logger.error(f"Erreur lors du nettoyage des métriques: {e}")
    
    def send_daily_report(self):
        """Envoie le rapport quotidien"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                devices = Device.query.all()
                
                stats = {
                    'total': len(devices),
                    'online': len([d for d in devices if d.status == 'online']),
                    'offline': len([d for d in devices if d.status == 'offline']),
                    'warning': len([d for d in devices if d.status == 'warning'])
                }
                
                self.notification_service.send_daily_report(stats)
                self.logger.info("Rapport quotidien envoyé")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'envoi du rapport quotidien: {e}")
    
    def add_device_monitoring(self, device_id):
        """Ajoute un appareil à la surveillance"""
        with self.app.app_context():
            device = Device.query.get(device_id)
            if device:
                self.previous_device_states[device_id] = device.status
                self.logger.info(f"Appareil {device.name} ajouté à la surveillance")
    
    def remove_device_monitoring(self, device_id):
        """Retire un appareil de la surveillance"""
        if device_id in self.previous_device_states:
            del self.previous_device_states[device_id]
            self.logger.info(f"Appareil {device_id} retiré de la surveillance")
    
    def get_scheduler_status(self):
        """Retourne le statut du planificateur"""
        if self.scheduler:
            return {
                'running': self.scheduler.running,
                'jobs': [
                    {
                        'id': job.id,
                        'name': job.name,
                        'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    for job in self.scheduler.get_jobs()
                ]
            }
        return {'running': False, 'jobs': []}