FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Installer les dépendances système nécessaires pour SNMP
RUN apt-get update && apt-get install -y \
    snmp \
    snmp-mibs-downloader \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser

# Créer le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Changer vers l'utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "run.py"]
