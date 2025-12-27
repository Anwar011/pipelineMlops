# Test de Déploiement - Pipeline MLOps

## ✅ État Actuel

### Prérequis Vérifiés
- ✅ **Docker** : Version 29.1.3 (actif)
- ✅ **Docker Compose** : v2.40.3
- ✅ **Python** : 3.14.2 (compatible)
- ✅ **kubectl** : v1.34.1
- ✅ **Minikube** : v1.37.0 (démarré)
- ✅ **Cluster Kubernetes** : v1.34.0 (Ready)
- ✅ **Storage Class** : `standard` (minikube-hostpath) ✅

### Configuration Minikube
```
Cluster: minikube
Node: Ready (control-plane)
StorageClass: standard (default)
```

## 🚀 Prêt pour le Déploiement

### Option 1: Test via GitHub Actions (Recommandé)

1. **Aller sur GitHub** → Actions → MLOps Pipeline
2. **Cliquer sur "Run workflow"** → workflow_dispatch
3. **Sélectionner la branche** (main)
4. **Cliquer sur "Run workflow"**

Le pipeline va :
1. Détecter les changements de données (ou forcer avec workflow_dispatch)
2. Préparer les données
3. Entraîner le modèle
4. Enregistrer dans MLflow
5. Récupérer le modèle
6. Build l'image Docker
7. Déployer sur Kubernetes

### Option 2: Test Local (Étape par étape)

#### 1. Tester MLflow
```bash
cd docker
docker-compose up -d mlflow
curl http://localhost:5000/health
```

#### 2. Tester l'Entraînement
```bash
export PYTHONPATH=.
python scripts/prepare_data.py
python src/training/train.py --config configs/config.yaml
```

#### 3. Tester la Récupération du Modèle
```bash
python scripts/get_latest_model.py
```

#### 4. Tester le Build Docker
```bash
docker build -t plant-disease-api:test -f docker/Dockerfile .
```

#### 5. Tester le Déploiement Kubernetes
```bash
# Déployer le namespace
kubectl apply -f k8s/namespace.yaml

# Créer le ConfigMap pour class_mapping
kubectl create configmap class-mapping-config \
  --from-file=class_mapping.yaml=data/class_mapping.yaml \
  -n plant-disease-mlops \
  --dry-run=client -o yaml | kubectl apply -f -

# Appliquer les manifests
kubectl apply -f k8s/

# Vérifier le statut
kubectl get pods -n plant-disease-mlops
kubectl get svc -n plant-disease-mlops
```

## 📊 Monitoring

### Vérifier les Pods
```bash
kubectl get pods -n plant-disease-mlops -w
```

### Voir les Logs
```bash
kubectl logs -f deployment/plant-disease-api -n plant-disease-mlops
```

### Accéder à l'API
```bash
# Obtenir l'URL NodePort
minikube service api-service -n plant-disease-mlops --url

# Ou directement
kubectl get svc api-service -n plant-disease-mlops
# Puis accéder via: http://<node-ip>:30080
```

## 🔍 Troubleshooting

### Pods en Pending
```bash
# Vérifier les PVC
kubectl get pvc -n plant-disease-mlops

# Vérifier les événements
kubectl describe pod <pod-name> -n plant-disease-mlops
```

### Erreur d'Image
```bash
# Vérifier que l'image existe localement
docker images | grep plant-disease-api

# Si besoin, charger l'image dans Minikube
minikube image load plant-disease-api:latest
```

### Problème de Storage Class
Le storage class `standard` est déjà configuré par défaut dans Minikube.
Si problème, vérifier :
```bash
kubectl get storageclass
```

## ✅ Checklist Finale

Avant de lancer le pipeline complet :

- [x] Minikube démarré et accessible
- [x] kubectl configuré
- [x] Docker actif
- [x] Namespace créé
- [ ] Modèle entraîné (sera fait par le pipeline)
- [ ] Image Docker buildée (sera fait par le pipeline)
- [ ] Déploiement testé

## 🎯 Prochaine Étape

**Lancer le pipeline via GitHub Actions !**

Le pipeline automatisera tout le processus de bout en bout.

