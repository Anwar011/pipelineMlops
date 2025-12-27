"""
Script de test complet des fonctionnalités après installation des dépendances.
"""

import sys
from pathlib import Path

def test_imports():
    """Test des imports principaux."""
    print("=" * 60)
    print("TESTS D'IMPORT")
    print("=" * 60)
    
    tests = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("fastapi", "FastAPI"),
        ("mlflow", "MLflow"),
        ("dvc", "DVC"),
        ("pandas", "Pandas"),
        ("sklearn", "Scikit-learn"),
        ("yaml", "PyYAML"),
    ]
    
    results = []
    for module_name, display_name in tests:
        try:
            if module_name == "yaml":
                import yaml as mod
            elif module_name == "sklearn":
                import sklearn as mod
            else:
                mod = __import__(module_name)
            version = getattr(mod, "__version__", "N/A")
            print(f"  [OK] {display_name:20} version: {version}")
            results.append(True)
        except ImportError as e:
            print(f"  [ERREUR] {display_name:20} - {e}")
            results.append(False)
    
    return all(results)


def test_project_modules():
    """Test des modules du projet."""
    print("\n" + "=" * 60)
    print("TESTS DES MODULES DU PROJET")
    print("=" * 60)
    
    tests = [
        ("src.data.preprocessing", "get_transforms"),
        ("src.data.dataset", "PlantDiseaseDataset"),
        ("src.models.resnet", "create_resnet18"),
        ("src.inference.predictor", "PlantDiseasePredictor"),
        ("src.inference.api", "app"),
    ]
    
    results = []
    for module_name, attr_name in tests:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            print(f"  [OK] {module_name}.{attr_name}")
            results.append(True)
        except Exception as e:
            print(f"  [ERREUR] {module_name}.{attr_name} - {e}")
            results.append(False)
    
    return all(results)


def test_model_functionality():
    """Test de la fonctionnalité du modèle."""
    print("\n" + "=" * 60)
    print("TESTS DE FONCTIONNALITE")
    print("=" * 60)
    
    try:
        import torch
        from src.models.resnet import create_resnet18
        
        print("  Test: Creation du modele ResNet18...")
        model = create_resnet18(num_classes=10, pretrained=False)
        print("    [OK] Modele cree")
        
        print("  Test: Forward pass...")
        x = torch.randn(1, 3, 224, 224)
        y = model(x)
        expected_shape = (1, 10)
        if y.shape == expected_shape:
            print(f"    [OK] Output shape correct: {y.shape}")
        else:
            print(f"    [ERREUR] Shape attendu {expected_shape}, obtenu {y.shape}")
            return False
        
        return True
    except Exception as e:
        print(f"  [ERREUR] {e}")
        return False


def test_preprocessing():
    """Test du preprocessing."""
    print("\n" + "=" * 60)
    print("TESTS DE PREPROCESSING")
    print("=" * 60)
    
    try:
        from src.data.preprocessing import get_transforms, preprocess_image_from_bytes
        from PIL import Image
        import io
        
        print("  Test: get_transforms...")
        transform = get_transforms(224, False)
        print("    [OK] Transform cree")
        
        print("  Test: preprocess_image_from_bytes...")
        img = Image.new('RGB', (224, 224), color='red')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        img_bytes = buf.getvalue()
        tensor = preprocess_image_from_bytes(img_bytes, 224)
        expected_shape = (1, 3, 224, 224)
        if tensor.shape == expected_shape:
            print(f"    [OK] Tensor shape correct: {tensor.shape}")
        else:
            print(f"    [ERREUR] Shape attendu {expected_shape}, obtenu {tensor.shape}")
            return False
        
        return True
    except Exception as e:
        print(f"  [ERREUR] {e}")
        return False


def test_config():
    """Test de la configuration."""
    print("\n" + "=" * 60)
    print("TESTS DE CONFIGURATION")
    print("=" * 60)
    
    try:
        import yaml
        config_path = Path("configs/config.yaml")
        
        if not config_path.exists():
            print(f"  [ERREUR] Fichier config non trouve: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['data', 'model', 'training', 'mlflow', 'inference']
        for key in required_keys:
            if key not in config:
                print(f"  [ERREUR] Cle manquante dans config: {key}")
                return False
        
        print("  [OK] Configuration valide")
        print(f"    Model: {config['model']['name']}")
        print(f"    Classes: {config['model']['num_classes']}")
        print(f"    Epochs: {config['training']['num_epochs']}")
        
        return True
    except Exception as e:
        print(f"  [ERREUR] {e}")
        return False


def main():
    """Fonction principale."""
    print("\n" + "=" * 60)
    print("TESTS DE FONCTIONNALITE COMPLETS")
    print("=" * 60)
    print()
    
    results = []
    
    # Tests d'import
    results.append(("Imports", test_imports()))
    
    # Tests des modules du projet
    results.append(("Modules projet", test_project_modules()))
    
    # Tests de fonctionnalité
    results.append(("Modele", test_model_functionality()))
    results.append(("Preprocessing", test_preprocessing()))
    results.append(("Configuration", test_config()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "[OK]" if passed else "[ERREUR]"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("[SUCCES] Tous les tests sont passes!")
        print("\nProchaines etapes:")
        print("  1. Telecharger les donnees dans data/raw/PlantVillage/")
        print("  2. Lancer: python scripts/prepare_data.py")
        print("  3. Entrainer: python src/training/train.py --config configs/config.yaml")
        return 0
    else:
        print("[ERREUR] Certains tests ont echoue.")
        return 1


if __name__ == "__main__":
    sys.exit(main())



