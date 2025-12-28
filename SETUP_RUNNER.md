# Guide de Setup - Self-Hosted Runner + Kubernetes

## ✅ GitHub Secrets

**AUCUN SECRET REQUIS** pour le moment ! Le pipeline utilise :
- Self-hosted runner (accès direct)
- Docker local
- MLflow local (localhost)
- Kubernetes local via kubectl

## 🐳 Prérequis sur le Runner

### 1. Docker & Docker Compose
```bash
# Vérifier
docker --version
docker-compose --version

# Si absent, installer Docker Desktop (Windows) ou Docker Engine (Linux)
```

### 2. Python 3.9+
```bash
# Vérifier
python3 --version

# Le pipeline installera automatiquement les dépendances Python
```

### 3. kubectl (pour Kubernetes)
```bash
# Windows (PowerShell)
choco install kubernetes-cli

# Ou télécharger depuis:
# https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

# Vérifier
kubectl version --client
```

## ☸️ Option 1: Minikube (Recommandé pour Développement)

### Installation Minikube

**Windows:**
```powershell
# Via Chocolatey
choco install minikube

# Ou télécharger depuis:
# https://minikube.sigs.k8s.io/docs/start/
```

**Linux:**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Démarrer Minikube

```bash
# Démarrer Minikube
minikube start

# Vérifier
kubectl cluster-info
kubectl get nodes

# Vérifier que le storage class est disponible
kubectl get storageclass
# Si 'standard' n'existe pas, créer ou modifier k8s/pvc.yaml
```

### Configuration Storage Class (si nécessaire)

Si le storage class 'standard' n'existe pas, modifier `k8s/pvc.yaml`:

```yaml
storageClassName: standard  # ou "minikube-hostpath" pour Minikube
```

Ou créer un storage class :
```bash
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: k8s.io/minikube-hostpath
EOF
```

## ☸️ Option 2: Cluster Kubernetes Externe

Si vous avez déjà un cluster Kubernetes (GKE, EKS, AKS, etc.) :

```bash
# Configurer kubectl pour pointer vers votre cluster
# (selon votre provider)

# Vérifier la connexion
kubectl cluster-info
kubectl get nodes

# Vérifier le storage class
kubectl get storageclass
# Ajuster k8s/pvc.yaml avec le bon storageClassName
```

## 🧪 Tester le Setup

### 1. Vérifier Docker
```bash
docker ps
docker-compose version
```

### 2. Vérifier Python
```bash
python3 --version
```

### 3. Vérifier kubectl + Kubernetes
```bash
# Si Minikube
minikube status
kubectl cluster-info

# Si cluster externe
kubectl cluster-info
kubectl get nodes
```

### 4. Démarrer les Services (Important!)

Les services doivent être démarrés avant le pipeline :

```bash
# Démarrer MLflow, Prometheus, Grafana
cd docker
docker-compose up -d

# Vérifier que MLflow est accessible
curl http://localhost:5000/health

# Services disponibles:
# - MLflow: http://localhost:5000
# - Prometheus: http://localhost:9090  
# - Grafana: http://localhost:3000
```

**Note**: Le pipeline GitHub Actions vérifiera que MLflow est accessible mais ne le démarrera pas automatiquement.

### 5. Test Complet du Pipeline

```bash
# 1. Tester le build Docker
docker build -t plant-disease-api:test -f docker/Dockerfile .

# 2. Tester kubectl
kubectl apply -f k8s/namespace.yaml

# 3. Si tout fonctionne, le pipeline GitHub Actions devrait marcher !
```

## 📝 Notes Importantes

### Minikube avec Docker Desktop
Si vous utilisez Docker Desktop avec Minikube, assurez-vous que :
- Docker Desktop utilise WSL2 (Windows)
- Minikube est démarré avec `minikube start`

### Storage Class
Le pipeline utilise `storageClassName: standard` dans `k8s/pvc.yaml`.
- Minikube : utilisez `minikube-hostpath` ou créez un storage class `standard`
- Cloud (GKE/EKS/AKS) : ajustez selon votre provider

### Ports Disponibles
Assurez-vous que ces ports sont libres sur le runner :
- `5000` : MLflow
- `8000` : API (local)
- `9090` : Prometheus (docker-compose)
- `3000` : Grafana (docker-compose)
- `30080` : API Kubernetes NodePort (si Minikube)

## 🚀 Prochaines Étapes

1. ✅ Installer Minikube (ou configurer cluster externe)
2. ✅ Démarrer Minikube : `minikube start`
3. ✅ Vérifier kubectl : `kubectl cluster-info`
4. ✅ Tester un déploiement : `kubectl apply -f k8s/namespace.yaml`
5. ✅ Lancer un workflow GitHub Actions manuellement pour tester

Une fois tout configuré, le pipeline sera prêt à fonctionner automatiquement !

