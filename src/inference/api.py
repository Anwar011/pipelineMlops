"""
API FastAPI pour l'inférence de détection de maladies végétales.
"""

import sys
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, Response
import uvicorn
from pathlib import Path
import yaml
import time
from typing import Optional

from .predictor import PlantDiseasePredictor
from .metrics import (
    prediction_requests_total,
    prediction_errors_total,
    prediction_duration_seconds,
    prediction_confidence,
    model_loaded,
    model_classes_total,
    generate_latest,
    CONTENT_TYPE_LATEST
)

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# Charger la configuration
def load_config(config_path="configs/config.yaml"):
    """Charge la configuration."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


config = load_config()
inference_config = config['inference']

# Créer l'application FastAPI
app = FastAPI(
    title="Plant Disease Detection API",
    description="API pour la détection de maladies végétales avec deep learning",
    version="1.0.0"
)

# Charger le modèle au démarrage
predictor = None


@app.on_event("startup")
async def load_model():
    """Charge le modèle au démarrage de l'API."""
    global predictor
    model_path = inference_config['model_path']
    device = inference_config['device']
    
    try:
        predictor = PlantDiseasePredictor(
            model_path=model_path,
            config_path="configs/config.yaml",
            device=device
        )
        print(f"[OK] Modele charge avec succes")
        # Mettre à jour les métriques
        model_loaded.set(1)
        model_classes_total.set(predictor.num_classes)
    except Exception as e:
        print(f"[ERREUR] Erreur lors du chargement du modele: {e}")
        model_loaded.set(0)
        raise


@app.get("/")
async def root():
    """Endpoint racine."""
    return {
        "message": "Plant Disease Detection API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    is_loaded = predictor is not None
    
    status = "healthy" if is_loaded else "unhealthy"
    status_code = 200 if is_loaded else 503
    
    response = {
        "status": status,
        "model_loaded": is_loaded
    }
    
    if is_loaded:
        response.update({
            "num_classes": predictor.num_classes,
            "device": str(predictor.device)
        })
    
    return JSONResponse(content=response, status_code=status_code)


@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Image de la feuille à analyser"),
    top_k: Optional[int] = 3
):
    """
    Prédit la maladie d'une plante à partir d'une image.
    
    Args:
        file: Fichier image (JPEG, PNG)
        top_k: Nombre de prédictions top à retourner (default: 3)
    
    Returns:
        dict: Prédiction avec classe, confidence et probabilités
    """
    if predictor is None:
        prediction_errors_total.labels(error_type='model_not_loaded').inc()
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    # Vérifier le type de fichier
    if not file.content_type.startswith('image/'):
        prediction_requests_total.labels(status='error').inc()
        prediction_errors_total.labels(error_type='invalid_file_type').inc()
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté: {file.content_type}. Utilisez une image (JPEG, PNG)"
        )
    
    try:
        # Lire l'image
        image_bytes = await file.read()
        
        # Vérifier la taille (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            prediction_requests_total.labels(status='error').inc()
            prediction_errors_total.labels(error_type='file_too_large').inc()
            raise HTTPException(status_code=400, detail="Image trop grande (max 10MB)")
        
        # Prédiction avec métriques
        start_time = time.time()
        with prediction_duration_seconds.time():
            result = predictor.predict(image_bytes, top_k=top_k or 3)
        
        # Enregistrer les métriques
        prediction_requests_total.labels(status='success').inc()
        prediction_confidence.observe(result['confidence'])
        
        # Calculer le temps de traitement
        processing_time = time.time() - start_time
        result['processing_time_ms'] = round(processing_time * 1000, 2)
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        prediction_requests_total.labels(status='error').inc()
        prediction_errors_total.labels(error_type='prediction_error').inc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Retourne des informations sur le modèle."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return {
        "num_classes": predictor.num_classes,
        "class_names": predictor.class_names[:10],  # Premiers 10 pour éviter réponse trop longue
        "device": str(predictor.device),
        "model_type": "ResNet18"
    }


@app.get("/metrics")
async def metrics():
    """Endpoint Prometheus pour les métriques."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run(
        "src.inference.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


