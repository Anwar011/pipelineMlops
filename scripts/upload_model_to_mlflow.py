"""
Script pour uploader un modèle local vers MLflow.
Utilisé pour compléter le workflow localement sans relancer l'entraînement.
"""

import sys
import argparse
from pathlib import Path
import torch
import mlflow
from datetime import datetime

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def upload_model_to_mlflow(model_path, tracking_uri, experiment_name):
    """
    Upload un modèle local vers MLflow.
    
    Args:
        model_path: Chemin vers le fichier .pth du modèle
        tracking_uri: URI de MLflow (ex: http://localhost:5000)
        experiment_name: Nom de l'expérience MLflow
    """
    model_path = Path(model_path)
    
    if not model_path.exists():
        print(f"[ERREUR] Le fichier {model_path} n'existe pas!")
        sys.exit(1)
    
    print(f"[OK] Chargement du modèle depuis {model_path}...")
    
    # Charger le checkpoint
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        print(f"[OK] Checkpoint chargé")
        print(f"     Num classes: {checkpoint.get('num_classes', 'N/A')}")
        print(f"     Val acc: {checkpoint.get('val_acc', 'N/A')}")
        print(f"     Epoch: {checkpoint.get('epoch', 'N/A')}")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger le checkpoint: {e}")
        sys.exit(1)
    
    # Se connecter à MLflow
    print(f"[OK] Connexion à MLflow ({tracking_uri})...")
    mlflow.set_tracking_uri(tracking_uri)
    
    try:
        mlflow.set_experiment(experiment_name)
    except Exception as e:
        print(f"[ATTENTION] Impossible de créer/trouver l'expérience: {e}")
        sys.exit(1)
    
    # Créer un nouveau run MLflow
    run_name = f"manual-upload-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    with mlflow.start_run(run_name=run_name):
        print(f"[OK] Run MLflow créé: {run_name}")
        
        # Logger les paramètres
        mlflow.log_params({
            'num_classes': checkpoint.get('num_classes', 15),
            'val_acc': checkpoint.get('val_acc', 0.0),
            'epoch': checkpoint.get('epoch', 0),
            'source': 'manual_upload',
            'model_path': str(model_path)
        })
        
        # Logger les métriques
        if 'val_acc' in checkpoint:
            mlflow.log_metric('val_accuracy', checkpoint['val_acc'])
        if 'epoch' in checkpoint:
            mlflow.log_metric('epoch', checkpoint['epoch'])
        
        # Logger le modèle comme artifact
        print(f"[OK] Upload du modèle vers MLflow...")
        try:
            mlflow.log_artifact(str(model_path), "checkpoint")
            print(f"[OK] Checkpoint uploadé: checkpoint/{model_path.name}")
            
            # Créer aussi un modèle complet dans le dossier model
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                model_file = Path(tmpdir) / "model.pth"
                torch.save(checkpoint, model_file)
                mlflow.log_artifact(str(model_file), "model")
                print(f"[OK] Modèle uploadé: model/model.pth")
            
            run_id = mlflow.active_run().info.run_id
            print(f"\n[SUCCES] Modèle uploadé avec succès!")
            print(f"         Run ID: {run_id}")
            print(f"         Run Name: {run_name}")
            print(f"         Expérience: {experiment_name}")
            print(f"\n         Voir dans MLflow UI: {tracking_uri}/#/experiments")
            
        except Exception as e:
            print(f"[ERREUR] Impossible d'uploader le modèle: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Uploader un modèle local vers MLflow")
    parser.add_argument("--model-path", default="models/best_model.pth", 
                       help="Chemin vers le fichier .pth du modèle")
    parser.add_argument("--tracking-uri", default="http://localhost:5000", 
                       help="MLflow tracking URI")
    parser.add_argument("--experiment-name", default="plant_disease_mvp", 
                       help="Nom de l'expérience MLflow")
    
    args = parser.parse_args()
    
    upload_model_to_mlflow(
        args.model_path,
        args.tracking_uri,
        args.experiment_name
    )


if __name__ == "__main__":
    main()

