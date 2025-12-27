"""
Script d'entraînement pour le modèle de détection de maladies végétales.
"""

import os
import sys
import argparse
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
import mlflow
import mlflow.pytorch
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from src.models.resnet import create_resnet18
from src.data.dataset import PlantDiseaseDataset

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_config(config_path):
    """Charge la configuration."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Entraîne le modèle pour une epoch."""
    model.train()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    
    pbar = tqdm(dataloader, desc="Training")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Métriques
        running_loss += loss.item()
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        
        # Update progress bar
        pbar.set_postfix({'loss': loss.item()})
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = accuracy_score(all_labels, all_preds)
    
    return epoch_loss, epoch_acc


def validate_epoch(model, dataloader, criterion, device):
    """Valide le modèle pour une epoch."""
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc="Validation")
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Métriques
            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({'loss': loss.item()})
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = accuracy_score(all_labels, all_preds)
    
    return epoch_loss, epoch_acc, all_preds, all_labels


def train(config_path):
    """Fonction principale d'entraînement."""
    # Charger la configuration
    config = load_config(config_path)
    data_config = config['data']
    model_config = config['model']
    training_config = config['training']
    mlflow_config = config['mlflow']
    
    # Device
    device = torch.device(training_config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu'))
    print(f"Utilisation du device: {device}")
    
    # Créer les répertoires
    save_dir = Path(training_config['save_dir'])
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # MLflow
    mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
    mlflow.set_experiment(mlflow_config['experiment_name'])
    
    with mlflow.start_run():
        # Log des paramètres
        mlflow.log_params({
            'model_name': model_config['name'],
            'num_classes': model_config['num_classes'],
            'pretrained': model_config['pretrained'],
            'batch_size': data_config['batch_size'],
            'learning_rate': training_config['learning_rate'],
            'num_epochs': training_config['num_epochs'],
            'image_size': data_config['image_size']
        })
        
        # Datasets
        print("Chargement des datasets...")
        train_dataset = PlantDiseaseDataset(
            metadata_path=data_config['metadata_path'],
            split='train',
            image_size=data_config['image_size'],
            augmentation=True
        )
        val_dataset = PlantDiseaseDataset(
            metadata_path=data_config['metadata_path'],
            split='val',
            image_size=data_config['image_size'],
            augmentation=False
        )
        
        # DataLoaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=data_config['batch_size'],
            shuffle=True,
            num_workers=2,
            pin_memory=True if device.type == 'cuda' else False
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=data_config['batch_size'],
            shuffle=False,
            num_workers=2,
            pin_memory=True if device.type == 'cuda' else False
        )
        
        print(f"Train: {len(train_dataset)} images")
        print(f"Val: {len(val_dataset)} images")
        
        # Modèle
        print(f"Création du modèle {model_config['name']}...")
        model = create_resnet18(
            num_classes=model_config['num_classes'],
            pretrained=model_config['pretrained']
        )
        model = model.to(device)
        
        # Loss et Optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=training_config['learning_rate'])
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        
        # Entraînement
        best_val_acc = 0.0
        best_model_path = save_dir / "best_model.pth"
        
        print("\nDébut de l'entraînement...")
        for epoch in range(training_config['num_epochs']):
            print(f"\nEpoch {epoch+1}/{training_config['num_epochs']}")
            
            # Train
            train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
            
            # Validation
            val_loss, val_acc, val_preds, val_labels = validate_epoch(model, val_loader, criterion, device)
            
            # Learning rate scheduler
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            # Log MLflow
            mlflow.log_metrics({
                'train_loss': train_loss,
                'train_accuracy': train_acc,
                'val_loss': val_loss,
                'val_accuracy': val_acc,
                'learning_rate': current_lr
            }, step=epoch)
            
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            print(f"LR: {current_lr:.6f}")
            
            # Sauvegarder le meilleur modèle
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_acc,
                    'num_classes': model_config['num_classes']
                }, best_model_path)
                print(f"[OK] Meilleur modele sauvegarde (Val Acc: {val_acc:.4f})")
                
                # Log le modèle dans MLflow (à chaque amélioration)
                # Gérer l'erreur si le Model Registry n'est pas disponible
                try:
                    mlflow.pytorch.log_model(model, "model")
                    print(f"[OK] Modele enregistre dans MLflow (Val Acc: {val_acc:.4f})")
                except Exception as e:
                    # Si le Model Registry n'est pas disponible, enregistrer le checkpoint comme artifact
                    print(f"[ATTENTION] Erreur lors de l'enregistrement MLflow Model Registry: {e}")
                    print("[INFO] Enregistrement du checkpoint comme artifact...")
                    try:
                        # Toujours enregistrer le checkpoint comme backup
                        mlflow.log_artifact(str(best_model_path), "checkpoint")
                        print(f"[OK] Checkpoint sauvegarde comme artifact dans MLflow (Val Acc: {val_acc:.4f})")
                    except Exception as e2:
                        print(f"[ERREUR] Impossible d'enregistrer le checkpoint dans MLflow: {e2}")
                        print("[INFO] Le modele est sauvegarde localement dans models/best_model.pth")
        
        print(f"\n[OK] Entrainement termine!")
        print(f"Meilleure validation accuracy: {best_val_acc:.4f}")
        print(f"Modèle sauvegardé dans: {best_model_path}")
        
        # S'assurer que le modèle final est toujours enregistré dans MLflow
        # (au cas où aucun modèle n'a été enregistré pendant l'entraînement)
        print("Verification de l'enregistrement du modele final dans MLflow...")
        
        # Vérifier si le modèle a déjà été enregistré
        try:
            # Charger le meilleur checkpoint et enregistrer dans MLflow
            checkpoint = torch.load(best_model_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # Enregistrer le modèle final dans MLflow
            try:
                mlflow.pytorch.log_model(model, "model")
                print(f"[OK] Modele final enregistre dans MLflow avec succes!")
            except Exception as e:
                # Si le Model Registry n'est pas disponible, enregistrer comme artifact
                print(f"[ATTENTION] Erreur lors de l'enregistrement MLflow (Model Registry): {e}")
                print("[INFO] Enregistrement du checkpoint comme artifact...")
                mlflow.log_artifact(str(best_model_path), "checkpoint")
                print(f"[OK] Checkpoint enregistre comme artifact dans MLflow!")
            
        except Exception as e:
            print(f"[ATTENTION] Erreur lors de l'enregistrement final dans MLflow: {e}")
            print("Le modèle devrait avoir été enregistré pendant l'entraînement.")
        
        # Rapport final sur validation
        print("\nRapport de classification (validation):")
        print(classification_report(val_labels, val_preds, digits=4))


def main():
    parser = argparse.ArgumentParser(description='Entraîner le modèle de détection de maladies végétales')
    parser.add_argument('--config', type=str, default='configs/config.yaml',
                       help='Chemin vers le fichier de configuration')
    args = parser.parse_args()
    
    train(args.config)


if __name__ == "__main__":
    main()


