# GitHub Actions CI/CD

## Configuration

Le pipeline CI/CD est configuré pour s'exécuter sur :
- Push vers les branches `main` et `develop`
- Pull requests vers `main`

## Jobs

### 1. Tests (`test`)
- **Matrice** : Python 3.9, 3.10, 3.11
- **Services** : PostgreSQL pour les tests
- **Étapes** :
  - Installation des dépendances système (SNMP, ping)
  - Installation des dépendances Python
  - Linting avec flake8
  - Vérification du formatage avec Black
  - Exécution des tests avec coverage
  - Upload des résultats vers Codecov

### 2. Build Docker (`docker-build`)
- Construction de l'image Docker
- Test de l'image construite
- Cache avec GitHub Actions

### 3. Scan de sécurité (`security-scan`)
- Scan des vulnérabilités avec Trivy
- Upload des résultats vers GitHub Security

### 4. Déploiement (`deploy`)
- **Condition** : Push vers `main` uniquement
- Construction et push de l'image Docker
- Tags : `latest` et SHA du commit

## Secrets requis

Configurez ces secrets dans votre repository GitHub :

```bash
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
```

## Commandes locales

```bash
# Exécuter les tests
pytest tests/ -v --cov=app

# Vérifier le linting
flake8 .

# Formater le code
black .

# Tests complets comme dans CI
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=html
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127
black --check .
```

## Structure des tests

