#!/bin/bash

echo "🐳 Démarrage du Système de Surveillance Réseau avec Docker"
echo "=========================================================="

# Créer les répertoires nécessaires
mkdir -p data logs

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "Veuillez installer Docker : https://docs.docker.com/get-docker/"
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    echo "Veuillez installer Docker Compose : https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker et Docker Compose détectés"

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo "⚠️  Veuillez modifier le fichier .env selon vos besoins"
fi

# Construire et démarrer les conteneurs
echo "🔄 Construction des images Docker..."
docker-compose build

echo "🚀 Démarrage des conteneurs..."
docker-compose up -d

echo ""
echo "✅ Application démarrée avec succès!"
echo "🌐 Accédez à l'application : http://localhost:5000"
echo ""
echo "📋 Commandes utiles:"
echo "  docker-compose logs -f       # Voir les logs"
echo "  docker-compose stop          # Arrêter l'application"
echo "  docker-compose down          # Arrêter et supprimer les conteneurs"
echo "  docker-compose restart       # Redémarrer l'application"
