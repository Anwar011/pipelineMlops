#!/bin/bash
# Script de déploiement Kubernetes simple - API uniquement

set -e

NAMESPACE="plant-disease-mlops"
K8S_DIR="k8s"

echo "========================================="
echo "  Déploiement Kubernetes - API"
echo "========================================="
echo ""

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl n'est pas installé."
    exit 1
fi

# Vérifier la connexion
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Impossible de se connecter au cluster Kubernetes."
    exit 1
fi

echo "✅ Connexion au cluster réussie"
echo ""

# Créer le namespace
echo "📦 Création du namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"
echo ""

# Créer le ConfigMap pour class_mapping si le fichier existe
if [ -f "data/class_mapping.yaml" ]; then
    echo "📝 Création du ConfigMap..."
    kubectl create configmap class-mapping-config \
        --from-file=class_mapping.yaml=data/class_mapping.yaml \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    echo ""
fi

# Appliquer les manifests
echo "🚀 Déploiement de l'API..."
kubectl apply -f "$K8S_DIR/configmap.yaml"
kubectl apply -f "$K8S_DIR/pvc.yaml"
kubectl apply -f "$K8S_DIR/api-deployment.yaml"
kubectl apply -f "$K8S_DIR/api-service.yaml"
echo ""

# Attendre que les pods soient prêts
echo "⏳ Attente du démarrage..."
kubectl wait --for=condition=ready pod -l app=plant-disease-api -n "$NAMESPACE" --timeout=300s || true
echo ""

# Statut
echo "📊 Statut:"
kubectl get pods -n "$NAMESPACE"
kubectl get svc -n "$NAMESPACE"
echo ""

echo "✅ Déploiement terminé!"
echo ""
echo "Pour accéder à l'API:"
echo "  NodePort: http://<node-ip>:30080"
echo ""
