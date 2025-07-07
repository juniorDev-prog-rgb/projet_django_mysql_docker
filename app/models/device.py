from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False, unique=True)
    device_type = db.Column(db.String(50), nullable=False)  # router, switch, server, etc.
    status = db.Column(db.String(20), default='unknown')  # online, offline, warning, unknown
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Informations SNMP
    snmp_community = db.Column(db.String(50), default='public')
    snmp_version = db.Column(db.String(10), default='2c')
    
    # Métriques de performance
    cpu_usage = db.Column(db.Float, default=0.0)
    memory_usage = db.Column(db.Float, default=0.0)
    uptime = db.Column(db.BigInteger, default=0)
    
    # Relations
    metrics = db.relationship('DeviceMetric', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.name} ({self.ip_address})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'uptime': self.uptime,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DeviceMetric(db.Model):
    __tablename__ = 'device_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, bandwidth, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))  # %, MB, Mbps, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<DeviceMetric {self.metric_type}: {self.value}{self.unit}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'metric_type': self.metric_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat()
        }