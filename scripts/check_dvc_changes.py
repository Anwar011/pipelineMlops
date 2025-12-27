"""
Script pour vérifier les changements DVC et écrire dans GITHUB_OUTPUT.
Utilisé dans le workflow GitHub Actions pour contourner les problèmes avec cmd/PowerShell.
"""

import os
import subprocess
import sys

def main():
    # Vérifier si workflow_dispatch
    event_name = os.environ.get('GITHUB_EVENT_NAME', '')
    
    if event_name == 'workflow_dispatch':
        result = 'true'
        print("Changements de donnees detectes ou trigger manuel")
    else:
        # Ajouter le PATH local pour DVC
        user_profile = os.environ.get('USERPROFILE', os.environ.get('HOME', ''))
        local_bin = os.path.join(user_profile, '.local', 'bin')
        if local_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{local_bin}{os.pathsep}{os.environ.get('PATH', '')}"
        
        # Vérifier les changements DVC
        try:
            result = subprocess.run(
                ['dvc', 'status', 'data/raw.dvc'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Chercher si des changements sont détectés
            if 'changed' in result.stdout or 'data/raw.dvc' in result.stdout:
                result = 'true'
                print("Changements de donnees detectes")
            else:
                result = 'false'
                print("Pas de changements de donnees")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            # Si DVC n'est pas disponible ou erreur, considérer comme pas de changements
            result = 'false'
            print(f"Pas de changements de donnees (DVC non disponible ou erreur: {e})")
    
    # Écrire dans GITHUB_OUTPUT
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"changed={result}\n")
    else:
        print(f"GITHUB_OUTPUT non defini, changed={result}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()

