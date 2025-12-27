"""
Script pour initialiser et configurer DVC.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Exécute une commande shell."""
    print(f"Exécution: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"Erreur: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and not check:
        print(result.stderr)
    
    return result


def main():
    """Initialise DVC."""
    print("Initialisation de DVC...")
    
    # Vérifier si DVC est installé
    # Essayer d'abord avec dvc direct, puis avec python -m dvc
    result = run_command("dvc --version", check=False)
    if result.returncode != 0:
        result = run_command("python -m dvc --version", check=False)
        if result.returncode != 0:
            print("[ERREUR] DVC n'est pas installe. Installez-le avec: pip install dvc")
            sys.exit(1)
    
    # Initialiser DVC (sans SCM pour MVP)
    run_command("dvc init --no-scm")
    
    # Créer .dvcignore
    dvcignore_content = """# Patterns à ignorer pour DVC
*.pyc
__pycache__/
*.log
mlruns/
models/*.pth
.env
"""
    Path(".dvcignore").write_text(dvcignore_content)
    print("[OK] .dvcignore cree")
    
    # Configurer le remote storage local
    run_command("dvc remote add -d storage .dvc/storage", check=False)
    
    # Instructions
    print("\n" + "="*60)
    print("DVC initialise avec succes!")
    print("="*60)
    print("\nStockage: Local (.dvc/storage/)")
    print("\nProchaines etapes:")
    print("1. Ajoutez les donnees a DVC:")
    print("   dvc add data/raw/")
    print("   dvc add data/processed/")
    print("\n2. Commit dans Git (si utilise):")
    print("   git add data/*.dvc .gitignore .dvcignore")
    print("   git commit -m \"Add data with DVC\"")
    print("\nPour verifier le statut:")
    print("   dvc status")
    print("="*60)


if __name__ == "__main__":
    main()


