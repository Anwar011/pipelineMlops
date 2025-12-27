"""
Module pour charger le modèle et faire des prédictions.
"""

import sys
import torch
import torch.nn.functional as F
from pathlib import Path
import yaml
from PIL import Image
import numpy as np

from src.models.resnet import create_resnet18
from src.data.preprocessing import preprocess_image_from_bytes

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class PlantDiseasePredictor:
    """
    Classe pour charger et utiliser le modèle de prédiction.
    """
    
    def __init__(self, model_path, config_path="configs/config.yaml", device="cpu"):
        """
        Args:
            model_path: Chemin vers le modèle sauvegardé (.pth)
            config_path: Chemin vers le fichier de configuration
            device: Device à utiliser ('cpu' ou 'cuda')
        """
        self.device = torch.device(device)
        self.config = self._load_config(config_path)
        self.model = None
        self.class_names = None
        self.num_classes = None
        
        # Charger le modèle
        self._load_model(model_path)
        
        # Charger le mapping des classes
        self._load_class_mapping()
    
    def _load_config(self, config_path):
        """Charge la configuration."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def _load_model(self, model_path):
        """Charge le modèle depuis le fichier sauvegardé."""
        checkpoint_path = Path(model_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
        
        # Charger le checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # Récupérer le nombre de classes depuis le checkpoint ou config
        self.num_classes = checkpoint.get('num_classes', self.config['model']['num_classes'])
        
        # Créer le modèle
        self.model = create_resnet18(
            num_classes=self.num_classes,
            pretrained=False  # Pas besoin de pretrained pour l'inférence
        )
        
        # Charger les poids
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"[OK] Modele charge depuis {model_path}")
        print(f"   Device: {self.device}")
        print(f"   Classes: {self.num_classes}")
    
    def _load_class_mapping(self):
        """Charge le mapping des classes depuis le fichier YAML."""
        mapping_path = Path("data/class_mapping.yaml")
        if mapping_path.exists():
            with open(mapping_path, 'r') as f:
                mapping_data = yaml.safe_load(f)
            id_to_class_raw = mapping_data.get('id_to_class', {})
            # S'assurer que les clés sont des entiers
            self.id_to_class = {int(k): v for k, v in id_to_class_raw.items()}
            self.class_names = list(self.id_to_class.values())
        else:
            # Fallback: générer des noms génériques
            self.id_to_class = {i: f"class_{i}" for i in range(self.num_classes)}
            self.class_names = list(self.id_to_class.values())
            print(f"[WARN] Fichier class_mapping.yaml non trouve, utilisation de noms generiques")
    
    def predict(self, image_bytes, top_k=3):
        """
        Prédit la classe d'une image.
        
        Args:
            image_bytes: Bytes de l'image
            top_k: Nombre de prédictions top à retourner
        
        Returns:
            dict: Dictionnaire avec prédiction, confidence, et probabilités
        """
        # Preprocessing
        image_size = self.config['data']['image_size']
        input_tensor = preprocess_image_from_bytes(image_bytes, image_size)
        input_tensor = input_tensor.to(self.device)
        
        # Prédiction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            
            # Top k prédictions
            top_probs, top_indices = torch.topk(probabilities, min(top_k, self.num_classes), dim=1)
        
        # Convertir en numpy
        top_probs = top_probs.cpu().numpy()[0]
        top_indices = top_indices.cpu().numpy()[0]
        
        # Construire le résultat
        result = {
            'prediction': self.id_to_class.get(int(top_indices[0]), f"class_{top_indices[0]}"),
            'class_id': int(top_indices[0]),
            'confidence': float(top_probs[0]),
            'probabilities': {}
        }
        
        # Ajouter les top k probabilités
        for idx, prob in zip(top_indices, top_probs):
            class_name = self.id_to_class.get(int(idx), f"class_{idx}")
            result['probabilities'][class_name] = float(prob)
        
        return result
    
    def predict_from_path(self, image_path, top_k=3):
        """
        Prédit depuis un chemin d'image.
        
        Args:
            image_path: Chemin vers l'image
            top_k: Nombre de prédictions top
        
        Returns:
            dict: Résultat de la prédiction
        """
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return self.predict(image_bytes, top_k)

