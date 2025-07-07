import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///network_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration SNMP
    SNMP_COMMUNITY = os.environ.get('SNMP_COMMUNITY') or 'public'
    SNMP_PORT = int(os.environ.get('SNMP_PORT') or 161)
    SNMP_TIMEOUT = int(os.environ.get('SNMP_TIMEOUT') or 5)
    
    # Configuration de surveillance
    MONITORING_INTERVAL = int(os.environ.get('MONITORING_INTERVAL') or 30)  # en secondes
    
    # Configuration des notifications
    EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')