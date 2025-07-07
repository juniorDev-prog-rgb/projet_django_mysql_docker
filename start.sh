#!/bin/bash

echo "🚀 Démarrage du Système de Surveillance Réseau"
echo "================================================"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "Exécutez d'abord: python setup.py"
    exit 1
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "Copie du fichier d'exemple..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo "📝 Veuillez modifier le fichier .env selon vos besoins"
fi

# Démarrer l'application
echo "🌐 Démarrage de l'application sur http://localhost:5000"
echo "⏹️  Appuyez sur Ctrl+C pour arrêter"
echo ""
python run.py
