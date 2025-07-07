import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app
import logging

class NotificationService:
    """Service pour l'envoi de notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, body, is_html=False):
        """Envoie un email"""
        try:
            if not current_app.config.get('EMAIL_ENABLED'):
                self.logger.info("Notifications email désactivées")
                return False
            
            smtp_server = current_app.config.get('SMTP_SERVER')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            username = current_app.config.get('SMTP_USERNAME')
            password = current_app.config.get('SMTP_PASSWORD')
            
            if not all([smtp_server, username, password]):
                self.logger.error("Configuration SMTP incomplète")
                return False
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Ajouter le corps du message
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Envoyer l'email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            text = msg.as_string()
            server.sendmail(username, to_email, text)
            server.quit()
            
            self.logger.info(f"Email envoyé avec succès à {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def notify_device_down(self, device):
        """Notifie qu'un appareil est hors ligne"""
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if not admin_email:
            return False
        
        subject = f"[ALERTE] Appareil hors ligne: {device.name}"
        body = f"""
        Bonjour,
        
        L'appareil suivant est actuellement hors ligne:
        
        Nom: {device.name}
        Adresse IP: {device.ip_address}
        Type: {device.device_type}
        Dernière vue: {device.last_seen}
        
        Veuillez vérifier la connectivité de cet appareil.
        
        Cordialement,
        Système de surveillance réseau
        """
        
        return self.send_email(admin_email, subject, body)
    
    def notify_device_up(self, device):
        """Notifie qu'un appareil est de nouveau en ligne"""
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if not admin_email:
            return False
        
        subject = f"[INFO] Appareil de nouveau en ligne: {device.name}"
        body = f"""
        Bonjour,
        
        L'appareil suivant est de nouveau en ligne:
        
        Nom: {device.name}
        Adresse IP: {device.ip_address}
        Type: {device.device_type}
        Rétabli le: {datetime.utcnow()}
        
        Cordialement,
        Système de surveillance réseau
        """
        
        return self.send_email(admin_email, subject, body)
    
    def notify_high_cpu_usage(self, device, cpu_usage):
        """Notifie d'une utilisation CPU élevée"""
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if not admin_email:
            return False
        
        subject = f"[ATTENTION] Utilisation CPU élevée: {device.name}"
        body = f"""
        Bonjour,
        
        L'appareil suivant présente une utilisation CPU élevée:
        
        Nom: {device.name}
        Adresse IP: {device.ip_address}
        Utilisation CPU: {cpu_usage}%
        Détecté le: {datetime.utcnow()}
        
        Il est recommandé de vérifier l'état de cet appareil.
        
        Cordialement,
        Système de surveillance réseau
        """
        
        return self.send_email(admin_email, subject, body)
    
    def notify_high_memory_usage(self, device, memory_usage):
        """Notifie d'une utilisation mémoire élevée"""
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if not admin_email:
            return False
        
        subject = f"[ATTENTION] Utilisation mémoire élevée: {device.name}"
        body = f"""
        Bonjour,
        
        L'appareil suivant présente une utilisation mémoire élevée:
        
        Nom: {device.name}
        Adresse IP: {device.ip_address}
        Utilisation mémoire: {memory_usage}%
        Détecté le: {datetime.utcnow()}
        
        Il est recommandé de vérifier l'état de cet appareil.
        
        Cordialement,
        Système de surveillance réseau
        """
        
        return self.send_email(admin_email, subject, body)
    
    def send_daily_report(self, devices_stats):
        """Envoie un rapport quotidien"""
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if not admin_email:
            return False
        
        total = devices_stats.get('total', 0)
        online = devices_stats.get('online', 0)
        offline = devices_stats.get('offline', 0)
        warning = devices_stats.get('warning', 0)
        
        subject = f"Rapport quotidien - Surveillance réseau ({datetime.utcnow().strftime('%d/%m/%Y')})"
        body = f"""
        Bonjour,
        
        Voici le rapport quotidien de surveillance réseau:
        
        STATISTIQUES GÉNÉRALES:
        - Total des appareils: {total}
        - Appareils en ligne: {online}
        - Appareils hors ligne: {offline}
        - Appareils en avertissement: {warning}
        
        Taux de disponibilité: {(online/total*100):.1f}% ({online}/{total})
        
        Ce rapport a été généré automatiquement le {datetime.utcnow().strftime('%d/%m/%Y à %H:%M')}.
        
        Cordialement,
        Système de surveillance réseau
        """
        
        return self.send_email(admin_email, subject, body)