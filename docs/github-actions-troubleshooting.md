# Guide de dépannage GitHub Actions

## Erreurs corrigées

### 1. CodeQL Action v2 deprecated
**Erreur**: `CodeQL Action major versions v1 and v2 have been deprecated`
**Solution**: Mise à jour vers `github/codeql-action/upload-sarif@v3`

### 2. Resource not accessible by integration
**Erreur**: `Resource not accessible by integration`
**Solution**: Ajout des permissions appropriées dans le workflow

```yaml
permissions:
  contents: read
  security-events: write
  actions: read
```

## Configuration des secrets

Dans votre repository GitHub, configurez ces secrets :

### Obligatoires pour le déploiement
```
DOCKER_USERNAME: your-docker-username
DOCKER_PASSWORD: your-docker-password
```

### Optionnels pour les notifications
```
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/...
```

## Workflows disponibles

### 1. CI/CD Principal (`.github/workflows/ci.yml`)
- Tests sur Python 3.9, 3.10, 3.11
- Build et test Docker
- Scan de sécurité Trivy
- Déploiement automatique sur main

### 2. Scan de sécurité (`.github/workflows/security.yml`)
- Scan Trivy du filesystem
- Scan Trivy de l'image Docker
- Vérification des dépendances avec Safety
- Exécution programmée tous les lundis

### 3. Tests de performance (`.github/workflows/performance.yml`)
- Tests de charge basiques
- Vérification des temps de réponse
- Déclenchement manuel ou sur PR

### 4. Notifications (`.github/workflows/notify.yml`)
- Notifications Slack des résultats CI/CD
- Optionnel - nécessite SLACK_WEBHOOK_URL

## Résolution de problèmes

### Échec des tests
```bash
# Exécuter localement
pytest tests/ -v --cov=app
flake8 .
black --check .
```

### Échec du build Docker
```bash
# Tester localement
docker build -t network-monitoring:test .
docker run --rm -p 5000:5000 network-monitoring:test
```

### Problèmes de permissions
1. Vérifier les permissions du workflow
2. Vérifier les secrets du repository
3. Contacter l'administrateur si nécessaire

### Scan de sécurité qui échoue
1. Vérifier que les permissions `security-events: write` sont présentes
2. S'assurer que GitHub Advanced Security est activé
3. Les résultats apparaissent dans l'onglet "Security" du repository
```
