Write-Host "🐳 Démarrage du Système de Surveillance Réseau avec Docker" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# Créer les répertoires nécessaires
if (!(Test-Path "data")) { New-Item -ItemType Directory -Path "data" }
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }

# Vérifier si Docker est installé
try {
    docker --version | Out-Null
    Write-Host "✅ Docker détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    Write-Host "Veuillez installer Docker Desktop : https://docs.docker.com/desktop/windows/" -ForegroundColor Yellow
    exit 1
}

# Vérifier si Docker Compose est installé
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose n'est pas installé" -ForegroundColor Red
    exit 1
}

# Créer le fichier .env s'il n'existe pas
if (!(Test-Path ".env")) {
    Write-Host "📝 Création du fichier .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
    Write-Host "⚠️  Veuillez modifier le fichier .env selon vos besoins" -ForegroundColor Yellow
}

# Construire et démarrer les conteneurs
Write-Host "🔄 Construction des images Docker..." -ForegroundColor Blue
docker-compose build

Write-Host "🚀 Démarrage des conteneurs..." -ForegroundColor Blue
docker-compose up -d

Write-Host ""
Write-Host "✅ Application démarrée avec succès!" -ForegroundColor Green
Write-Host "🌐 Accédez à l'application : http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Commandes utiles:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f       # Voir les logs"
Write-Host "  docker-compose stop          # Arrêter l'application"
Write-Host "  docker-compose down          # Arrêter et supprimer les conteneurs"
Write-Host "  docker-compose restart       # Redémarrer l'application"
