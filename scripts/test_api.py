"""
Script pour tester l'API de prédiction.
"""

import sys
import requests
import time
from pathlib import Path
import yaml

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000"
TEST_IMAGE_PATH = None


def find_test_image():
    """Trouve une image de test."""
    global TEST_IMAGE_PATH
    
    # Chercher dans les données brutes
    raw_dir = Path("data/raw/PlantVillage")
    if raw_dir.exists():
        for img_file in raw_dir.rglob("*.jpg"):
            TEST_IMAGE_PATH = img_file
            return TEST_IMAGE_PATH
        for img_file in raw_dir.rglob("*.JPG"):
            TEST_IMAGE_PATH = img_file
            return TEST_IMAGE_PATH
    
    return None


def test_health():
    """Teste l'endpoint /health."""
    print("\n[TEST] Health Check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Status: {data.get('status')}")
            print(f"   [OK] Model loaded: {data.get('model_loaded')}")
            if data.get('model_loaded'):
                print(f"   [OK] Num classes: {data.get('num_classes')}")
                print(f"   [OK] Device: {data.get('device')}")
            return True
        else:
            print(f"   [ERREUR] Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   [ERREUR] Impossible de se connecter a {API_URL}")
        print(f"   Assurez-vous que l'API est demarree:")
        print(f"   python scripts/run_api.py")
        return False
    except Exception as e:
        print(f"   [ERREUR] {e}")
        return False


def test_root():
    """Teste l'endpoint racine."""
    print("\n[TEST] Root endpoint...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Message: {data.get('message')}")
            print(f"   [OK] Version: {data.get('version')}")
            return True
        else:
            print(f"   [ERREUR] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERREUR] {e}")
        return False


def test_model_info():
    """Teste l'endpoint /model/info."""
    print("\n[TEST] Model info...")
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Num classes: {data.get('num_classes')}")
            print(f"   [OK] Device: {data.get('device')}")
            print(f"   [OK] Model type: {data.get('model_type')}")
            class_names = data.get('class_names', [])
            if class_names:
                print(f"   [OK] Classes (first 5): {', '.join(class_names[:5])}")
            return True
        else:
            print(f"   [ERREUR] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERREUR] {e}")
        return False


def test_predict():
    """Teste l'endpoint /predict."""
    print("\n[TEST] Prediction...")
    
    # Trouver une image de test
    test_image = find_test_image()
    if not test_image or not Path(test_image).exists():
        print(f"   [ERREUR] Aucune image de test trouvee")
        print(f"   Placez une image dans data/raw/PlantVillage/")
        return False
    
    print(f"   Image de test: {test_image.name}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image.name, f, 'image/jpeg')}
            response = requests.post(
                f"{API_URL}/predict",
                files=files,
                params={'top_k': 3},
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Prediction: {data.get('prediction')}")
            print(f"   [OK] Confidence: {data.get('confidence'):.4f}")
            print(f"   [OK] Processing time: {data.get('processing_time_ms'):.2f} ms")
            
            probabilities = data.get('probabilities', {})
            if probabilities:
                print(f"   [OK] Top 3 predictions:")
                for i, (class_name, prob) in enumerate(list(probabilities.items())[:3], 1):
                    print(f"      {i}. {class_name}: {prob:.4f}")
            
            return True
        else:
            print(f"   [ERREUR] Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   [ERREUR] {e}")
        return False


def main():
    """Fonction principale."""
    print("=" * 60)
    print("TEST DE L'API DE PREDICTION")
    print("=" * 60)
    print(f"\nAPI URL: {API_URL}")
    print("\nAttente de 2 secondes pour s'assurer que l'API est prete...")
    time.sleep(2)
    
    results = []
    
    # Tests
    results.append(("Health Check", test_health()))
    results.append(("Root endpoint", test_root()))
    results.append(("Model info", test_model_info()))
    results.append(("Prediction", test_predict()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[ECHEC]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests reussis")
    
    if passed == total:
        print("\n[SUCCES] Tous les tests sont passes!")
        return 0
    else:
        print(f"\n[ATTENTION] {total - passed} test(s) ont echoue")
        return 1


if __name__ == "__main__":
    sys.exit(main())


