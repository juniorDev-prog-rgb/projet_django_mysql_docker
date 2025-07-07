@echo off
echo 🚀 Démarrage du Système de Surveillance Réseau
echo ================================================

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo ❌ Environnement virtuel non trouvé
    echo Exécutez d'abord: python setup.py
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé
    echo Copie du fichier d'exemple...
    copy .env.example .env
    echo ✅ Fichier .env créé
    echo 📝 Veuillez modifier le fichier .env selon vos besoins
)

REM Démarrer l'application
echo 🌐 Démarrage de l'application sur http://localhost:5000
echo ⏹️  Appuyez sur Ctrl+C pour arrêter
echo.
python run.py

pause
