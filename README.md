# Pipeline MLOps - Détection de Maladies Végétales

Pipeline MLOps complet avec CI/CD automatique : détection des nouvelles données → entraînement → déploiement.

## 🎯 Vue d'ensemble

Pipeline automatisé qui :
1. **Détecte** les nouvelles données versionnées avec DVC
2. **Entraîne** le modèle sur les nouvelles données
3. **Stocke** le modèle dans MLflow
4. **Récupère** le dernier modèle depuis MLflow
5. **Build** l'image Docker de l'API
6. **Déploie** sur Kubernetes

## 📁 Structure

```
pipelineMlops/
├── .github/workflows/      # Pipeline CI/CD GitHub Actions
├── configs/                # Configuration
├── data/                   # Données (versionnées avec DVC)
├── docker/                 # Docker & docker-compose
├── k8s/                    # Manifests Kubernetes (API uniquement)
├── models/                 # Modèles entraînés
├── scripts/                # Scripts utilitaires
└── src/                    # Code source
    ├── data/              # Preprocessing & Dataset
    ├── models/            # Architecture modèle
    ├── training/          # Script d'entraînement
    └── inference/         # API FastAPI
```

## 🚀 Quick Start

### 1. Préparation des données

```bash
# Préparer les données (split, metadata)
python scripts/prepare_data.py

# Versionner avec DVC
dvc add data/raw
git add data/raw.dvc .gitignore
git commit -m "Add data"
```

### 2. Démarrer les services (MLflow, Prometheus, Grafana)

```bash
# Démarrer tous les services en conteneurs
cd docker
docker-compose up -d

# Services disponibles:
# - MLflow: http://localhost:5000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
```

### 3. Entraînement local

```bash
# Assurez-vous que MLflow est accessible (voir étape 2)

# Entraîner
export PYTHONPATH=.
python src/training/train.py --config configs/config.yaml

# Récupérer le dernier modèle depuis MLflow
python scripts/get_latest_model.py
```

### 4. API locale

```bash
# Option 1: Docker Compose
cd docker
docker-compose up

# Option 2: Directement
python scripts/run_api.py
```

### 5. Déploiement Kubernetes

```bash
# Déployer l'API
chmod +x scripts/deploy-k8s.sh
./scripts/deploy-k8s.sh

# Accès: http://<node-ip>:30080
```

## 🔄 Pipeline CI/CD

### Déclenchement automatique

Le pipeline se déclenche automatiquement quand :
- Push de `data/raw.dvc` ou changements dans `.dvc/`
- Push de nouvelles données dans `data/raw/`

### Déclenchement manuel

Dans GitHub Actions : "Run workflow" → "workflow_dispatch"

### Workflow

1. **Checkout** du code
2. **Détection** des changements de données (DVC)
3. **Préparation** des données
4. **Entraînement** du modèle
5. **Récupération** du modèle depuis MLflow
6. **Build** de l'image Docker
7. **Déploiement** Kubernetes (si runner local configuré)

## 🐳 Docker Compose

Services disponibles :
- **MLflow** : http://localhost:5000 (tracking des expériences)
- **API** : http://localhost:8000 (prédictions)
- **Prometheus** : http://localhost:9090 (métriques)
- **Grafana** : http://localhost:3000 (dashboard, admin/admin)

```bash
cd docker
docker-compose up -d
```

## ☸️ Kubernetes

Déploiement simple de l'API uniquement :
- **Deployment** : 2 replicas
- **Service** : NodePort (port 30080)
- **PVC** : Stockage des modèles

```bash
kubectl apply -f k8s/
```

## 📊 Monitoring

- **Prometheus** : Métriques système et API
- **Grafana** : Dashboards (à configurer)
- **MLflow** : Tracking des expériences ML

## 📝 Configuration

Fichier principal : `configs/config.yaml`

- Données : paths, splits, batch size
- Modèle : architecture, classes
- Entraînement : epochs, learning rate
- MLflow : tracking URI, experiment name
- Inférence : device, model path

## 🔧 Prérequis

- Python 3.9+
- Docker & Docker Compose
- Kubernetes (Minikube ou cluster)
- kubectl (pour déploiement K8s)
- DVC (pour versioning des données)

## 📚 Documentation

- **README.md** : Ce fichier (vue d'ensemble)
- **scripts/** : Scripts avec documentation inline

## 🎯 Pipeline Complet

```
Nouvelles données (DVC) 
    ↓
GitHub Actions (détection)
    ↓
Entraînement (train.py)
    ↓
MLflow (stockage modèle)
    ↓
Récupération modèle (get_latest_model.py)
    ↓
Build Docker (Dockerfile)
    ↓
Déploiement Kubernetes (k8s/)
```
