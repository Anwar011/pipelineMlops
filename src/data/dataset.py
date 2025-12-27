"""
Dataset PyTorch pour les images de plantes.
"""

import pandas as pd
from torch.utils.data import Dataset
from PIL import Image
from pathlib import Path
from .preprocessing import get_transforms


class PlantDiseaseDataset(Dataset):
    """
    Dataset pour les images de maladies végétales.
    """
    
    def __init__(self, metadata_path, split=None, transform=None, image_size=224, augmentation=False):
        """
        Args:
            metadata_path: Chemin vers le fichier metadata.csv
            split: 'train', 'val', 'test', ou None pour tous
            transform: Transformations personnalisées (optionnel)
            image_size: Taille des images
            augmentation: Si True, utilise des augmentations pour train
        """
        self.metadata = pd.read_csv(metadata_path)
        self.image_size = image_size
        
        # Filtrer par split si spécifié
        if split:
            self.metadata = self.metadata[self.metadata['split'] == split].reset_index(drop=True)
        
        # Utiliser les transformations fournies ou créer des default
        if transform is None:
            self.transform = get_transforms(image_size, augmentation=(augmentation and split == 'train'))
        else:
            self.transform = transform
    
    def __len__(self):
        return len(self.metadata)
    
    def __getitem__(self, idx):
        """
        Retourne une image et son label.
        
        Returns:
            image (torch.Tensor): Image transformée
            label (int): ID de la classe
        """
        row = self.metadata.iloc[idx]
        image_path = row['path']
        label = int(row['class_id'])
        
        # Charger l'image
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de {image_path}: {e}")
        
        # Appliquer les transformations
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_class_names(self):
        """Retourne la liste des noms de classes."""
        return sorted(self.metadata['label'].unique().tolist())



