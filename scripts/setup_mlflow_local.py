"""
Script pour démarrer MLflow localement (alternative au conteneur).
Utilisez ce script si vous préférez ne pas utiliser Docker pour MLflow.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Démarre MLflow UI localement."""
    print("Démarrage de MLflow UI...")
    print("URI: http://localhost:5000")
    print("\nPour arrêter, appuyez sur Ctrl+C\n")
    
    # Créer le dossier mlruns si nécessaire
    Path("mlruns").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    
    # Commande MLflow
    cmd = [
        sys.executable, "-m", "mlflow", "ui",
        "--host", "0.0.0.0",
        "--port", "5000",
        "--backend-store-uri", "file:./mlruns",
        "--default-artifact-root", "file:./models"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nMLflow arrêté.")


if __name__ == "__main__":
    main()

