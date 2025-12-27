"""
Script pour copier automatiquement les données vers le runner si elles n'existent pas.
Utilisé dans le workflow GitHub Actions pour automatiser la copie.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    # Chemin du workspace du runner (où le code est checkout)
    workspace = os.environ.get('GITHUB_WORKSPACE', '.')
    
    # Chemin source (repo local où les données sont versionnées)
    # Si on est dans un runner, on cherche dans le repo parent ou on utilise le workspace
    # Pour un self-hosted runner, les données peuvent être dans le repo checkout
    
    # Chemin de destination dans le workspace
    target_data_path = Path(workspace) / "data" / "raw" / "PlantVillage"
    
    # Chemins possibles pour les données source
    source_paths = [
        # Option 1: Données déjà dans le workspace (checkout normal)
        Path(workspace) / "data" / "raw" / "PlantVillage",
        # Option 2: Repo local (si runner est sur la même machine)
        Path.home() / "pipelineMlops" / "data" / "raw" / "PlantVillage",
        # Option 3: Chemin relatif depuis le workspace
        Path(workspace).parent.parent.parent / "pipelineMlops" / "data" / "raw" / "PlantVillage",
    ]
    
    # Vérifier si les données existent déjà
    if target_data_path.exists():
        print(f"[OK] Les donnees existent deja dans le workspace: {target_data_path}")
        return 0
    
    # Chercher les données source
    source_path = None
    for path in source_paths:
        if path.exists() and path.is_dir():
            source_path = path
            print(f"[OK] Donnees source trouvees: {source_path}")
            break
    
    if not source_path:
        print(f"[ERREUR] Impossible de trouver les donnees source")
        print(f"Chemins verifies:")
        for path in source_paths:
            print(f"  - {path}")
        return 1
    
    # Copier les données
    print(f"[INFO] Copie des donnees vers: {target_data_path}")
    print(f"  Cela peut prendre quelques minutes...")
    
    try:
        # Créer le répertoire parent
        target_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copier
        shutil.copytree(source_path, target_data_path, dirs_exist_ok=True)
        print(f"[OK] Donnees copiees avec succes!")
        return 0
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la copie: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

