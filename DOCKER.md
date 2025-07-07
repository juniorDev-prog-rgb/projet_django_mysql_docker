# Guide Docker pour le Système de Surveillance Réseau

## Démarrage rapide

### Avec Docker Compose (Recommandé)

1. **Installation des prérequis :**
   - [Docker Desktop](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

2. **Cloner et configurer :**
   ```bash
   git clone <votre-repo>
   cd network_monitoring
   cp .env.example .env
   # Modifier .env selon vos besoins
   ```

3. **Démarrer l'application :**
   ```bash
   # Linux/Mac
   ./docker-start.sh
   
   # Windows
   .\docker-start.ps1
   
   # Ou manuellement
   docker-compose up -d
   ```

4. **Accéder à l'application :**
   Ouvrez http://localhost:5000

## Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose stop

# Redémarrer
docker-compose restart

# Supprimer tout
docker-compose down

# Reconstruire les images
docker-compose build --no-cache
```

## Configuration pour la production

1. **Utiliser le fichier de production :**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Variables d'environnement importantes :**
   ```bash
   SECRET_KEY=your-production-secret-key
   EMAIL_ENABLED=true
   SMTP_SERVER=your-smtp-server
   ADMIN_EMAIL=admin@yourdomain.com
   ```

## Volumes et persistance

- **Base de données :** `/app/data/network_monitoring.db`
- **Logs :** `/app/logs/`
- **Configuration :** Variables d'environnement

## Résolution de problèmes

### L'application ne démarre pas
```bash
# Vérifier les logs
docker-compose logs web

# Vérifier le statut
docker-compose ps
```

### Problèmes de permissions
```bash
# Reconstruire avec les bonnes permissions
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Réinitialiser complètement
```bash
docker-compose down -v
docker system prune -f
docker-compose up -d
```
