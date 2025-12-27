"""
Script de test pour vérifier la structure et la syntaxe du projet.
Ne nécessite pas l'installation des dépendances.
"""

import os
import ast
import sys
from pathlib import Path

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def check_file_exists(filepath):
    """Vérifie si un fichier existe."""
    return Path(filepath).exists()


def check_python_syntax(filepath):
    """Vérifie la syntaxe Python d'un fichier."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Erreur: {e}"


def main():
    """Fonction principale de test."""
    print("=" * 60)
    print("TEST DE STRUCTURE ET SYNTAXE DU PROJET")
    print("=" * 60)
    print()
    
    # Liste des fichiers essentiels
    essential_files = [
        "configs/config.yaml",
        "requirements.txt",
        ".gitignore",
        ".dvcignore",
        "src/__init__.py",
        "src/data/__init__.py",
        "src/data/dataset.py",
        "src/data/preprocessing.py",
        "src/models/__init__.py",
        "src/models/resnet.py",
        "src/training/__init__.py",
        "src/training/train.py",
        "src/inference/__init__.py",
        "src/inference/api.py",
        "src/inference/predictor.py",
        "scripts/prepare_data.py",
        "scripts/setup_dvc.py",
        "scripts/run_api.py",
        "docker/Dockerfile",
    ]
    
    # Liste des dossiers essentiels
    essential_dirs = [
        "configs",
        "data/raw",
        "data/processed",
        "src/data",
        "src/models",
        "src/training",
        "src/inference",
        "scripts",
        "docker",
        "models",
    ]
    
    print("1. Verification des dossiers...")
    dirs_ok = True
    for dir_path in essential_dirs:
        if Path(dir_path).exists():
            print(f"   [OK] {dir_path}/")
        else:
            print(f"   [ERREUR] {dir_path}/ (manquant)")
            dirs_ok = False
    
    print()
    print("2. Verification des fichiers...")
    files_ok = True
    for file_path in essential_files:
        if check_file_exists(file_path):
            print(f"   [OK] {file_path}")
        else:
            print(f"   [ERREUR] {file_path} (manquant)")
            files_ok = False
    
    print()
    print("3. Verification de la syntaxe Python...")
    python_files = [f for f in essential_files if f.endswith('.py')]
    syntax_ok = True
    for file_path in python_files:
        if check_file_exists(file_path):
            is_valid, error = check_python_syntax(file_path)
            if is_valid:
                print(f"   [OK] {file_path} (syntaxe OK)")
            else:
                print(f"   [ERREUR] {file_path} (erreur de syntaxe: {error})")
                syntax_ok = False
    
    print()
    print("4. Verification de la structure des modules...")
    modules_ok = True
    
    # Verifier les imports relatifs
    try:
        # Verifier que les __init__.py existent
        init_files = [
            "src/__init__.py",
            "src/data/__init__.py",
            "src/models/__init__.py",
            "src/training/__init__.py",
            "src/inference/__init__.py",
        ]
        for init_file in init_files:
            if check_file_exists(init_file):
                print(f"   [OK] {init_file}")
            else:
                print(f"   [ERREUR] {init_file} (manquant)")
                modules_ok = False
    except Exception as e:
        print(f"   [ATTENTION] Erreur lors de la verification: {e}")
        modules_ok = False
    
    print()
    print("=" * 60)
    print("RESUME")
    print("=" * 60)
    
    all_ok = dirs_ok and files_ok and syntax_ok and modules_ok
    
    if all_ok:
        print("[SUCCES] Tous les tests de structure sont passes!")
        print()
        print("Prochaines etapes:")
        print("   1. Installer les dependances: pip install -r requirements.txt")
        print("   2. Telecharger les donnees dans data/raw/PlantVillage/")
        print("   3. Lancer: python scripts/prepare_data.py")
        print("   4. Entrainer: python src/training/train.py --config configs/config.yaml")
        return 0
    else:
        print("[ERREUR] Certains tests ont echoue. Verifiez les erreurs ci-dessus.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

