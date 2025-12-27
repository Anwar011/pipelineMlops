"""
Script utilitaire pour lancer l'API facilement.
"""

import uvicorn
import sys
from pathlib import Path

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    # Vérifier que le modèle existe
    config_path = Path("configs/config.yaml")
    if not config_path.exists():
        print("[ERREUR] Fichier config.yaml non trouve!")
        sys.exit(1)
    
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    model_path = Path(config['inference']['model_path'])
    if not model_path.exists():
        print(f"[WARN] Modele non trouve: {model_path}")
        print("   Assurez-vous d'avoir entraine le modele d'abord:")
        print("   python src/training/train.py --config configs/config.yaml")
        response = input("\nContinuer quand meme? (o/n): ")
        if response.lower() != 'o':
            sys.exit(1)
    
    print("[OK] Demarrage de l'API...")
    print("   Documentation: http://localhost:8000/docs")
    print("   Health check: http://localhost:8000/health")
    print("\nAppuyez sur Ctrl+C pour arreter\n")
    
    uvicorn.run(
        "src.inference.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


