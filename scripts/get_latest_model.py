"""
Récupère le dernier modèle enregistré depuis MLflow.
"""

import sys
import mlflow
import mlflow.pytorch
from pathlib import Path
import torch

def get_latest_model(tracking_uri, experiment_name, output_file="models/best_model.pth"):
    """
    Récupère le dernier modèle PyTorch depuis MLflow et le sauvegarde.
    
    Args:
        tracking_uri: URI de MLflow (ex: http://localhost:5000)
        experiment_name: Nom de l'expérience
        output_file: Fichier de sortie pour le modèle (.pth)
    """
    # Se connecter à MLflow
    mlflow.set_tracking_uri(tracking_uri)
    client = mlflow.tracking.MlflowClient()
    
    # Trouver l'expérience
    try:
        experiment = client.get_experiment_by_name(experiment_name)
        if experiment is None:
            raise ValueError(f"Expérience '{experiment_name}' non trouvée")
    except Exception as e:
        print(f"[ERREUR] Impossible de trouver l'expérience: {e}")
        sys.exit(1)
    
    # Obtenir le dernier run
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        raise ValueError("Aucun run trouvé dans l'expérience")
    
    latest_run = runs[0]
    run_id = latest_run.info.run_id
    
    print(f"[OK] Dernier run trouvé: {run_id}")
    print(f"     Date: {latest_run.info.start_time}")
    print(f"     Val Accuracy: {latest_run.data.metrics.get('val_accuracy', 'N/A')}")
    
    # URI du modèle dans MLflow
    model_uri = f"runs:/{run_id}/model"
    
    print(f"[OK] Téléchargement du modèle depuis MLflow...")
    
    # Charger le modèle PyTorch depuis MLflow
    try:
        model = mlflow.pytorch.load_model(model_uri)
        
        # Sauvegarder le modèle au format PyTorch standard
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Récupérer les métadonnées du run pour la sauvegarde
        num_classes = latest_run.data.params.get('num_classes', 15)
        try:
            num_classes = int(num_classes)
        except:
            num_classes = 15
        
        # Récupérer val_acc depuis les métriques
        val_acc = float(latest_run.data.metrics.get('val_accuracy', 0.0))
        
        # Sauvegarder le checkpoint PyTorch (format compatible avec predictor.py)
        checkpoint = {
            'model_state_dict': model.state_dict(),
            'num_classes': num_classes,
            'val_acc': val_acc,
            'epoch': latest_run.data.metrics.get('epoch', 0)
        }
        
        torch.save(checkpoint, output_path)
        print(f"[OK] Modèle sauvegardé vers: {output_path}")
        print(f"     Num classes: {num_classes}")
        print(f"     Val Accuracy: {val_acc:.4f}")
        return str(output_path)
        
    except Exception as e:
        print(f"[ERREUR] Impossible de charger le modèle: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Récupérer le dernier modèle MLflow")
    parser.add_argument("--tracking-uri", default="http://localhost:5000", help="MLflow tracking URI")
    parser.add_argument("--experiment-name", default="plant_disease_mvp", help="Nom de l'expérience")
    parser.add_argument("--output-file", default="models/best_model.pth", help="Fichier de sortie")
    
    args = parser.parse_args()
    
    try:
        model_path = get_latest_model(
            args.tracking_uri,
            args.experiment_name,
            args.output_file
        )
        print(f"\n[SUCCES] Modèle récupéré: {model_path}")
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        sys.exit(1)
