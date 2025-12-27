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
    model = None
    num_classes = latest_run.data.params.get('num_classes', 15)
    try:
        num_classes = int(num_classes)
    except:
        num_classes = 15
    
    try:
        # Essayer de charger depuis le modèle enregistré
        model = mlflow.pytorch.load_model(model_uri)
        print(f"[OK] Modèle chargé depuis MLflow")
    except Exception as e:
        # Si le modèle n'est pas disponible, essayer de charger depuis le checkpoint artifact
        print(f"[INFO] Modèle principal non disponible ({e}), tentative depuis checkpoint...")
        checkpoint_uri = f"runs:/{run_id}/checkpoint/best_model.pth"
        try:
            # Télécharger le checkpoint
            checkpoint_path = mlflow.artifacts.download_artifacts(checkpoint_uri)
            # Charger le checkpoint directement
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            # Extraire num_classes du checkpoint si disponible
            if 'num_classes' in checkpoint:
                num_classes = checkpoint['num_classes']
            # Reconstruire le modèle
            import sys
            from pathlib import Path
            # Ajouter le répertoire parent au path pour les imports
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.models.resnet import create_resnet18
            model = create_resnet18(num_classes=num_classes, pretrained=False)
            model.load_state_dict(checkpoint['model_state_dict'])
            print(f"[OK] Modèle chargé depuis checkpoint artifact")
        except Exception as e2:
            # Dernier recours: chercher dans tous les artifacts
            print(f"[INFO] Tentative depuis les artifacts disponibles...")
            try:
                artifacts = client.list_artifacts(run_id)
                checkpoint_found = False
                for artifact in artifacts:
                    if 'best_model.pth' in artifact.path or 'checkpoint' in artifact.path:
                        artifact_uri = f"runs:/{run_id}/{artifact.path}"
                        checkpoint_path = mlflow.artifacts.download_artifacts(artifact_uri)
                        checkpoint = torch.load(checkpoint_path, map_location='cpu')
                        if 'num_classes' in checkpoint:
                            num_classes = checkpoint['num_classes']
                        import sys
                        from pathlib import Path
                        sys.path.insert(0, str(Path(__file__).parent.parent))
                        from src.models.resnet import create_resnet18
                        model = create_resnet18(num_classes=num_classes, pretrained=False)
                        model.load_state_dict(checkpoint['model_state_dict'])
                        checkpoint_found = True
                        print(f"[OK] Modèle chargé depuis artifact: {artifact.path}")
                        break
                if not checkpoint_found:
                    raise Exception(f"Impossible de trouver un checkpoint. Erreurs: {e}, {e2}")
            except Exception as e3:
                raise Exception(f"Impossible de charger le modèle depuis MLflow. Erreurs: {e}, {e2}, {e3}")
        
    if model is None:
        raise Exception("Impossible de charger le modèle depuis MLflow")
    
    # Sauvegarder le modèle au format PyTorch standard
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
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
