// Dashboard JavaScript
class NetworkMonitoring {
    constructor() {
        this.socket = null;
        this.autoRefresh = true;
        this.devices = [];
        this.initializeWebSocket();
        this.bindEvents();
    }

    initializeWebSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connecté au serveur WebSocket');
            this.socket.emit('join_monitoring');
        });

        this.socket.on('disconnect', () => {
            console.log('Déconnecté du serveur WebSocket');
            this.showAlert('warning', 'Connexion temps réel perdue. Tentative de reconnexion...', false);
        });

        this.socket.on('devices_update', (devices) => {
            this.devices = devices;
            this.updateDevicesTable();
        });

        this.socket.on('device_update', (device) => {
            this.updateSingleDevice(device);
        });

        this.socket.on('stats_update', (stats) => {
            this.updateStats(stats);
        });

        this.socket.on('alert', (alert) => {
            this.showAlert(alert.type, alert.message, true, alert.device);
        });

        this.socket.on('metrics_update', (data) => {
            this.updateDeviceMetrics(data.device_id, data.metrics);
        });
    }

    bindEvents() {
        // Auto-refresh toggle
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            this.autoRefresh = e.target.checked;
            if (this.autoRefresh) {
                this.socket.emit('join_monitoring');
            } else {
                this.socket.emit('leave_monitoring');
            }
        });

        // Form submission
        document.getElementById('addDeviceForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addDevice();
        });
    }

    showAlert(type, message, dismissible = true, device = null) {
        const alertsContainer = document.getElementById('alerts-container');
        const alertId = 'alert-' + Date.now();
        
        let icon = 'fas fa-info-circle';
        if (type === 'error') icon = 'fas fa-exclamation-triangle';
        if (type === 'warning') icon = 'fas fa-exclamation-circle';
        if (type === 'success') icon = 'fas fa-check-circle';

        const alertHtml = `
            <div class="alert alert-${type === 'error' ? 'danger' : type} ${dismissible ? 'alert-dismissible' : ''} fade show" 
                 id="${alertId}" role="alert">
                <i class="${icon} me-2"></i>
                <strong>${this.getAlertTitle(type)}:</strong> ${message}
                ${device ? `<br><small>Appareil: ${device.name} (${device.ip_address})</small>` : ''}
                ${dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' : ''}
            </div>
        `;

        alertsContainer.insertAdjacentHTML('afterbegin', alertHtml);

        // Auto-remove after 5 seconds if dismissible
        if (dismissible) {
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    getAlertTitle(type) {
        switch (type) {
            case 'error': return 'Erreur';
            case 'warning': return 'Attention';
            case 'success': return 'Succès';
            case 'info': return 'Information';
            default: return 'Notification';
        }
    }

    updateStats(stats) {
        document.getElementById('total-devices').textContent = stats.total;
        document.getElementById('online-devices').textContent = stats.online;
        document.getElementById('offline-devices').textContent = stats.offline;
        document.getElementById('warning-devices').textContent = stats.warning;
    }

    updateDevicesTable() {
        const tbody = document.getElementById('devices-table-body');
        tbody.innerHTML = '';

        this.devices.forEach(device => {
            const row = this.createDeviceRow(device);
            tbody.appendChild(row);
        });
    }

    createDeviceRow(device) {
        const row = document.createElement('tr');
        row.setAttribute('data-device-id', device.id);

        const statusClass = device.status === 'online' ? 'success' : 
                           device.status === 'offline' ? 'danger' : 'warning';
        
        const statusIcon = device.status === 'online' ? 'check' : 
                          device.status === 'offline' ? 'times' : 'exclamation';

        const cpuBar = device.cpu_usage ? 
            `<div class="progress" style="height: 20px;">
                <div class="progress-bar bg-${device.cpu_usage > 80 ? 'danger' : device.cpu_usage > 60 ? 'warning' : 'success'}" 
                     style="width: ${device.cpu_usage}%">
                    ${device.cpu_usage.toFixed(1)}%
                </div>
            </div>` : '<span class="text-muted">N/A</span>';

        const memoryBar = device.memory_usage ? 
            `<div class="progress" style="height: 20px;">
                <div class="progress-bar bg-${device.memory_usage > 90 ? 'danger' : device.memory_usage > 70 ? 'warning' : 'success'}" 
                     style="width: ${device.memory_usage}%">
                    ${device.memory_usage.toFixed(1)}%
                </div>
            </div>` : '<span class="text-muted">N/A</span>';

        const lastSeen = device.last_seen ? 
            new Date(device.last_seen).toLocaleString('fr-FR') : 
            '<span class="text-muted">Jamais</span>';

        row.innerHTML = `
            <td>
                <span class="badge bg-${statusClass}">
                    <i class="fas fa-${statusIcon}"></i>
                    ${device.status.charAt(0).toUpperCase() + device.status.slice(1)}
                </span>
            </td>
            <td><strong>${device.name}</strong></td>
            <td><code>${device.ip_address}</code></td>
            <td>${device.device_type.charAt(0).toUpperCase() + device.device_type.slice(1)}</td>
            <td>${cpuBar}</td>
            <td>${memoryBar}</td>
            <td><small class="text-muted">${lastSeen}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="networkMonitoring.viewDevice(${device.id})" 
                            data-bs-toggle="modal" data-bs-target="#deviceModal">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-warning" onclick="networkMonitoring.editDevice(${device.id})"
                            data-bs-toggle="modal" data-bs-target="#editDeviceModal">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="networkMonitoring.testDevice(${device.id})">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="networkMonitoring.deleteDevice(${device.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        return row;
    }

    updateSingleDevice(device) {
        const row = document.querySelector(`tr[data-device-id="${device.id}"]`);
        if (row) {
            const newRow = this.createDeviceRow(device);
            row.parentNode.replaceChild(newRow, row);
            
            // Add pulse animation for updated device
            newRow.classList.add('pulse');
            setTimeout(() => newRow.classList.remove('pulse'), 2000);
        }

        // Update device in local array
        const index = this.devices.findIndex(d => d.id === device.id);
        if (index !== -1) {
            this.devices[index] = device;
        }
    }

    async addDevice() {
        const form = document.getElementById('addDeviceForm');
        const formData = new FormData(form);
        
        const deviceData = {
            name: document.getElementById('deviceName').value,
            ip_address: document.getElementById('deviceIP').value,
            device_type: document.getElementById('deviceType').value,
            snmp_community: document.getElementById('snmpCommunity').value
        };

        try {
            const response = await fetch('/api/devices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(deviceData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('success', `Appareil ${deviceData.name} ajouté avec succès`);
                bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
                form.reset();
                this.refreshDevices();
            } else {
                this.showAlert('error', result.error || 'Erreur lors de l\'ajout');
            }
        } catch (error) {
            this.showAlert('error', 'Erreur de connexion au serveur');
        }
    }

    async testDevice(deviceId) {
        try {
            const response = await fetch(`/api/devices/${deviceId}/test`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('success', result.message);
            } else {
                this.showAlert('error', result.error || 'Erreur lors du test');
            }
        } catch (error) {
            this.showAlert('error', 'Erreur de connexion au serveur');
        }
    }

    async deleteDevice(deviceId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet appareil ?')) {
            return;
        }

        try {
            const response = await fetch(`/api/devices/${deviceId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('success', 'Appareil supprimé avec succès');
                this.refreshDevices();
            } else {
                this.showAlert('error', result.error || 'Erreur lors de la suppression');
            }
        } catch (error) {
            this.showAlert('error', 'Erreur de connexion au serveur');
        }
    }

    async viewDevice(deviceId) {
        try {
            const response = await fetch(`/api/devices/${deviceId}`);
            const device = await response.json();

            if (response.ok) {
                this.displayDeviceDetails(device);
            } else {
                this.showAlert('error', 'Erreur lors du chargement des détails');
            }
        } catch (error) {
            this.showAlert('error', 'Erreur de connexion au serveur');
        }
    }

    displayDeviceDetails(device) {
        const detailsContainer = document.getElementById('deviceDetails');
        
        const statusClass = device.status === 'online' ? 'success' : 
                           device.status === 'offline' ? 'danger' : 'warning';

        detailsContainer.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Informations Générales</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Nom:</strong></td><td>${device.name}</td></tr>
                        <tr><td><strong>Adresse IP:</strong></td><td><code>${device.ip_address}</code></td></tr>
                        <tr><td><strong>Type:</strong></td><td>${device.device_type}</td></tr>
                        <tr><td><strong>Statut:</strong></td><td><span class="badge bg-${statusClass}">${device.status}</span></td></tr>
                        <tr><td><strong>Dernière vue:</strong></td><td>${device.last_seen ? new Date(device.last_seen).toLocaleString('fr-FR') : 'Jamais'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Métriques</h6>
                    <table class="table table-sm">
                        <tr><td><strong>CPU:</strong></td><td>${device.cpu_usage ? device.cpu_usage.toFixed(1) + '%' : 'N/A'}</td></tr>
                        <tr><td><strong>Mémoire:</strong></td><td>${device.memory_usage ? device.memory_usage.toFixed(1) + '%' : 'N/A'}</td></tr>
                        <tr><td><strong>Uptime:</strong></td><td>${device.uptime ? this.formatUptime(device.uptime) : 'N/A'}</td></tr>
                        <tr><td><strong>Communauté SNMP:</strong></td><td>${device.snmp_community || 'public'}</td></tr>
                        <tr><td><strong>Version SNMP:</strong></td><td>${device.snmp_version || '2c'}</td></tr>
                    </table>
                </div>
            </div>
        `;
    }

    formatUptime(centiseconds) {
        const seconds = Math.floor(centiseconds / 100);
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        return `${days}j ${hours}h ${minutes}m`;
    }

    async refreshDevices() {
        try {
            const response = await fetch('/api/devices');
            const devices = await response.json();

            if (response.ok) {
                this.devices = devices;
                this.updateDevicesTable();
                
                // Update stats
                const stats = {
                    total: devices.length,
                    online: devices.filter(d => d.status === 'online').length,
                    offline: devices.filter(d => d.status === 'offline').length,
                    warning: devices.filter(d => d.status === 'warning').length
                };
                this.updateStats(stats);
            }
        } catch (error) {
            this.showAlert('error', 'Erreur lors de l\'actualisation');
        }
    }

    editDevice(deviceId) {
        // TODO: Implement edit functionality
        this.showAlert('info', 'Fonctionnalité d\'édition en cours de développement');
    }

    updateDeviceMetrics(deviceId, metrics) {
        // TODO: Update metrics in real-time charts if implemented
        console.log('Metrics update for device', deviceId, metrics);
    }
}

// Global functions for onclick handlers
function refreshDevices() {
    networkMonitoring.refreshDevices();
}

function addDevice() {
    networkMonitoring.addDevice();
}

function viewDevice(deviceId) {
    networkMonitoring.viewDevice(deviceId);
}

function editDevice(deviceId) {
    networkMonitoring.editDevice(deviceId);
}

function testDevice(deviceId) {
    networkMonitoring.testDevice(deviceId);
}

function deleteDevice(deviceId) {
    networkMonitoring.deleteDevice(deviceId);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.networkMonitoring = new NetworkMonitoring();
});
