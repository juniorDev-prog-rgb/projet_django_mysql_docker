"""
Script de test pour vérifier la connectivité SNMP
Utilise ce script pour tester la connectivité SNMP avec vos appareils
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.snmp import SNMPService
from app.models.device import Device
import argparse

def test_snmp_connectivity(ip_address, community='public', port=161):
    """Teste la connectivité SNMP avec un appareil"""
    print(f"🔍 Test de connectivité SNMP vers {ip_address}")
    print(f"   Communauté: {community}")
    print(f"   Port: {port}")
    print("-" * 50)
    
    snmp_service = SNMPService()
    
    # Créer un objet Device temporaire pour le test
    device = type('Device', (), {
        'ip_address': ip_address,
        'snmp_community': community,
        'name': f'Test-{ip_address}',
        'id': 999
    })()
    
    try:
        # Test de connectivité de base
        print("🔸 Test de connectivité de base...")
        result = snmp_service.test_device_connectivity(device)
        if result['status'] == 'success':
            print(f"✅ Connectivité OK: {result['message']}")
            if 'system_name' in result:
                print(f"   Nom du système: {result['system_name']}")
        else:
            print(f"❌ Connectivité échouée: {result['message']}")
            return False
        
        # Test de collecte des métriques
        print("\n🔸 Test de collecte des métriques...")
        metrics_result = snmp_service.collect_device_metrics(device)
        
        if metrics_result['status'] == 'success':
            print(f"✅ Métriques collectées: {metrics_result['metrics_collected']} métriques")
            for metric in metrics_result.get('metrics', []):
                print(f"   - {metric['type']}: {metric['value']} {metric['unit']}")
        else:
            print(f"⚠️  Collecte partielle: {metrics_result.get('message', 'Erreur inconnue')}")
        
        # Test des OIDs individuels
        print("\n🔸 Test des OIDs individuels...")
        oids_to_test = {
            'Nom système': '1.3.6.1.2.1.1.5.0',
            'Description': '1.3.6.1.2.1.1.1.0',
            'Uptime': '1.3.6.1.2.1.1.3.0',
            'Contact': '1.3.6.1.2.1.1.4.0',
            'Location': '1.3.6.1.2.1.1.6.0'
        }
        
        for name, oid in oids_to_test.items():
            value = snmp_service.get_snmp_value(ip_address, oid, community, port)
            if value is not None:
                print(f"   ✅ {name}: {value}")
            else:
                print(f"   ❌ {name}: Non disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Test de connectivité SNMP')
    parser.add_argument('ip', help='Adresse IP de l\'appareil à tester')
    parser.add_argument('-c', '--community', default='public', help='Communauté SNMP (défaut: public)')
    parser.add_argument('-p', '--port', type=int, default=161, help='Port SNMP (défaut: 161)')
    
    args = parser.parse_args()
    
    print("🧪 Test de Connectivité SNMP")
    print("=" * 50)
    
    success = test_snmp_connectivity(args.ip, args.community, args.port)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test terminé avec succès!")
        print("✅ L'appareil peut être ajouté au système de surveillance")
    else:
        print("❌ Test échoué")
        print("🔧 Vérifiez:")
        print("   - L'adresse IP est correcte et accessible")
        print("   - SNMP est activé sur l'appareil")
        print("   - La communauté SNMP est correcte")
        print("   - Le port SNMP est ouvert (défaut: 161)")

if __name__ == "__main__":
    main()
