from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.device import Device, DeviceMetric, db
from app.services.snmp import SNMPService
from datetime import datetime, timedelta
import ipaddress

device_bp = Blueprint('devices', __name__)

@device_bp.route('/')
def dashboard():
    """Page d'accueil avec le tableau de bord"""
    devices = Device.query.all()
    
    # Statistiques générales
    total_devices = len(devices)
    online_devices = len([d for d in devices if d.status == 'online'])
    offline_devices = len([d for d in devices if d.status == 'offline'])
    warning_devices = len([d for d in devices if d.status == 'warning'])
    
    stats = {
        'total': total_devices,
        'online': online_devices,
        'offline': offline_devices,
        'warning': warning_devices
    }
    
    return render_template('dashboard.html', devices=devices, stats=stats)

@device_bp.route('/api/devices', methods=['GET'])
def get_devices():
    """API pour récupérer la liste des appareils"""
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices])

@device_bp.route('/api/devices', methods=['POST'])
def add_device():
    """API pour ajouter un nouvel appareil"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    # Validation des champs requis
    required_fields = ['name', 'ip_address', 'device_type']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    # Validation de l'adresse IP
    try:
        ipaddress.ip_address(data['ip_address'])
    except ValueError:
        return jsonify({'error': 'Adresse IP invalide'}), 400
    
    # Vérifier si l'appareil existe déjà
    existing_device = Device.query.filter_by(ip_address=data['ip_address']).first()
    if existing_device:
        return jsonify({'error': 'Un appareil avec cette adresse IP existe déjà'}), 409
    
    # Créer le nouvel appareil
    device = Device(
        name=data['name'],
        ip_address=data['ip_address'],
        device_type=data['device_type'],
        snmp_community=data.get('snmp_community', 'public'),
        snmp_version=data.get('snmp_version', '2c')
    )
    
    try:
        db.session.add(device)
        db.session.commit()
        
        # Tester la connectivité immédiatement
        snmp_service = SNMPService()
        snmp_service.test_device_connectivity(device)
        
        return jsonify(device.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'ajout de l\'appareil: {str(e)}'}), 500

@device_bp.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """API pour récupérer les détails d'un appareil"""
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict())

@device_bp.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """API pour mettre à jour un appareil"""
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    # Mise à jour des champs
    if 'name' in data:
        device.name = data['name']
    if 'device_type' in data:
        device.device_type = data['device_type']
    if 'snmp_community' in data:
        device.snmp_community = data['snmp_community']
    if 'snmp_version' in data:
        device.snmp_version = data['snmp_version']
    
    # Validation de l'adresse IP si elle est modifiée
    if 'ip_address' in data and data['ip_address'] != device.ip_address:
        try:
            ipaddress.ip_address(data['ip_address'])
            # Vérifier l'unicité
            existing = Device.query.filter_by(ip_address=data['ip_address']).first()
            if existing and existing.id != device.id:
                return jsonify({'error': 'Un appareil avec cette adresse IP existe déjà'}), 409
            device.ip_address = data['ip_address']
        except ValueError:
            return jsonify({'error': 'Adresse IP invalide'}), 400
    
    try:
        device.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(device.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@device_bp.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """API pour supprimer un appareil"""
    device = Device.query.get_or_404(device_id)
    
    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Appareil supprimé avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@device_bp.route('/api/devices/<int:device_id>/test', methods=['POST'])
def test_device(device_id):
    """API pour tester la connectivité d'un appareil"""
    device = Device.query.get_or_404(device_id)
    
    try:
        snmp_service = SNMPService()
        result = snmp_service.test_device_connectivity(device)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Erreur lors du test: {str(e)}'}), 500

@device_bp.route('/api/devices/<int:device_id>/metrics')
def get_device_metrics(device_id):
    """API pour récupérer les métriques d'un appareil"""
    device = Device.query.get_or_404(device_id)
    
    # Paramètres de requête
    hours = request.args.get('hours', 24, type=int)
    metric_type = request.args.get('type')
    
    # Calculer la date de début
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Construire la requête
    query = DeviceMetric.query.filter(
        DeviceMetric.device_id == device_id,
        DeviceMetric.timestamp >= start_time
    )
    
    if metric_type:
        query = query.filter(DeviceMetric.metric_type == metric_type)
    
    metrics = query.order_by(DeviceMetric.timestamp.desc()).all()
    
    return jsonify([metric.to_dict() for metric in metrics])