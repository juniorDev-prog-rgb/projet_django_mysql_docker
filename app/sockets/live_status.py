from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio
from app.models.device import Device
import json

@socketio.on('connect')
def handle_connect():
    """Gère les nouvelles connexions WebSocket"""
    print(f'Client connecté: {request.sid}')
    emit('status', {'message': 'Connexion établie'})

@socketio.on('disconnect')
def handle_disconnect():
    """Gère les déconnexions WebSocket"""
    print(f'Client déconnecté: {request.sid}')

@socketio.on('join_monitoring')
def handle_join_monitoring():
    """Le client rejoint la room de surveillance en temps réel"""
    join_room('monitoring')
    emit('status', {'message': 'Surveillance en temps réel activée'})
    
    # Envoyer l'état actuel de tous les appareils
    devices = Device.query.all()
    devices_data = [device.to_dict() for device in devices]
    emit('devices_update', devices_data)

@socketio.on('leave_monitoring')
def handle_leave_monitoring():
    """Le client quitte la room de surveillance en temps réel"""
    leave_room('monitoring')
    emit('status', {'message': 'Surveillance en temps réel désactivée'})

@socketio.on('request_device_status')
def handle_request_device_status(data):
    """Demande de statut pour un appareil spécifique"""
    device_id = data.get('device_id')
    if device_id:
        device = Device.query.get(device_id)
        if device:
            emit('device_status', device.to_dict())
        else:
            emit('error', {'message': 'Appareil non trouvé'})
    else:
        emit('error', {'message': 'ID d\'appareil requis'})

def broadcast_device_update(device):
    """Diffuse une mise à jour d'appareil à tous les clients connectés"""
    socketio.emit('device_update', device.to_dict(), room='monitoring')

def broadcast_devices_stats(stats):
    """Diffuse les statistiques générales à tous les clients connectés"""
    socketio.emit('stats_update', stats, room='monitoring')

def broadcast_alert(alert_type, message, device=None):
    """Diffuse une alerte à tous les clients connectés"""
    alert_data = {
        'type': alert_type,
        'message': message,
        'timestamp': Device.query.first().last_seen.isoformat() if Device.query.first() else None
    }
    
    if device:
        alert_data['device'] = device.to_dict()
    
    socketio.emit('alert', alert_data, room='monitoring')

def broadcast_metric_update(device_id, metrics):
    """Diffuse une mise à jour des métriques à tous les clients connectés"""
    socketio.emit('metrics_update', {
        'device_id': device_id,
        'metrics': metrics
    }, room='monitoring')