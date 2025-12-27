# Dockerfile optimisé avec multi-stage build pour l'API de détection de maladies végétales
FROM python:3.9-slim as builder

# Installer les outils de build nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement les requirements pour optimiser le cache Docker
COPY requirements-inference.txt .

# Installer les dépendances Python (torch CPU-only depuis l'index CPU)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch>=2.0.0 torchvision>=0.15.0 && \
    pip install --no-cache-dir -r requirements-inference.txt

# Stage final - image minimale
FROM python:3.9-slim

# Installer uniquement les dépendances runtime minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copier les packages Python depuis le builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Définir le répertoire de travail
WORKDIR /app

# Créer le répertoire data
RUN mkdir -p ./data

# Copier le code source (seulement ce qui est nécessaire pour l'inférence)
COPY src/ ./src/
COPY configs/ ./configs/
COPY models/ ./models/

# Copier le mapping des classes si disponible
COPY data/class_mapping.yaml ./data/class_mapping.yaml

# Variables d'environnement pour optimiser PyTorch
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OMP_NUM_THREADS=1

# Exposer le port
EXPOSE 8000

# Commande pour lancer l'API
CMD ["uvicorn", "src.inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
