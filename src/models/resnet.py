"""
Architecture ResNet18 pour la classification de maladies végétales.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.models.resnet as resnet_models


class ResNet18(nn.Module):
    """
    ResNet18 avec transfer learning pour classification multi-classes.
    """
    
    def __init__(self, num_classes=38, pretrained=True):
        """
        Args:
            num_classes: Nombre de classes à classifier
            pretrained: Si True, charge les poids pré-entraînés sur ImageNet
        """
        super(ResNet18, self).__init__()
        
        # Charger ResNet18 pré-entraîné (utiliser weights au lieu de pretrained pour éviter warning)
        if pretrained:
            weights = resnet_models.ResNet18_Weights.IMAGENET1K_V1
        else:
            weights = None
        self.model = models.resnet18(weights=weights)
        
        # Remplacer le dernier layer pour le nombre de classes souhaité
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, num_classes)
    
    def forward(self, x):
        """Forward pass."""
        return self.model(x)
    
    def get_model(self):
        """Retourne le modèle complet."""
        return self.model


def create_resnet18(num_classes=38, pretrained=True):
    """
    Factory function pour créer un ResNet18.
    
    Args:
        num_classes: Nombre de classes
        pretrained: Si True, utilise les poids ImageNet
    
    Returns:
        ResNet18: Modèle ResNet18
    """
    return ResNet18(num_classes=num_classes, pretrained=pretrained)


