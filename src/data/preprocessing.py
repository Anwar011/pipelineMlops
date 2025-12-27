"""
Fonctions de preprocessing pour les images.
"""

import torch
from torchvision import transforms
from PIL import Image
import numpy as np


def get_transforms(image_size=224, augmentation=False):
    """
    Retourne les transformations pour preprocessing.
    
    Args:
        image_size: Taille cible des images
        augmentation: Si True, ajoute des augmentations pour l'entraînement
    
    Returns:
        transforms.Compose: Composition de transformations
    """
    if augmentation:
        # Augmentations pour l'entraînement
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomRotation(30),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    else:
        # Transformations pour validation/test/inference
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    
    return transform


def preprocess_image(image_path, image_size=224):
    """
    Preprocess une image pour l'inférence.
    
    Args:
        image_path: Chemin vers l'image
        image_size: Taille cible
    
    Returns:
        torch.Tensor: Image préprocessée (1, 3, H, W)
    """
    transform = get_transforms(image_size, augmentation=False)
    
    # Charger l'image
    image = Image.open(image_path).convert('RGB')
    
    # Appliquer les transformations
    tensor = transform(image)
    
    # Ajouter une dimension batch
    tensor = tensor.unsqueeze(0)
    
    return tensor


def preprocess_image_from_bytes(image_bytes, image_size=224):
    """
    Preprocess une image depuis des bytes (pour l'API).
    
    Args:
        image_bytes: Bytes de l'image
        image_size: Taille cible
    
    Returns:
        torch.Tensor: Image préprocessée (1, 3, H, W)
    """
    from io import BytesIO
    
    transform = get_transforms(image_size, augmentation=False)
    
    # Charger l'image depuis bytes
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    
    # Appliquer les transformations
    tensor = transform(image)
    
    # Ajouter une dimension batch
    tensor = tensor.unsqueeze(0)
    
    return tensor



