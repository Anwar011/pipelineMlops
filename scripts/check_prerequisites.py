"""
Script de vérification des prérequis pour le pipeline MLOps.
"""

import sys
import subprocess
import os
from pathlib import Path

# Configurer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def run_command(cmd, shell=False):
    """Exécute une commande et retourne le résultat."""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(
                cmd,
                shell=True if shell or sys.platform == 'win32' else False,
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Vérifie si Docker est installé."""
    print("\n" + "="*60)
    print("1. VÉRIFICATION DE DOCKER")
    print("="*60)
    
    # Docker
    success, stdout, stderr = run_command("docker --version")
    if success:
        version = stdout.split('\n')[0] if stdout else "Version inconnue"
        print(f"   [✓] Docker installé: {version}")
    else:
        print(f"   [✗] Docker non trouvé")
        print(f"       Installation: https://www.docker.com/products/docker-desktop")
        return False
    
    # Docker Compose
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        version = stdout.split('\n')[0] if stdout else "Version inconnue"
        print(f"   [✓] Docker Compose installé: {version}")
    else:
        # Essayer avec 'docker compose' (v2)
        success, stdout, stderr = run_command("docker compose version")
        if success:
            version = stdout.split('\n')[0] if stdout else "Version inconnue"
            print(f"   [✓] Docker Compose (v2) installé: {version}")
        else:
            print(f"   [✗] Docker Compose non trouvé")
            return False
    
    # Test Docker daemon
    success, stdout, stderr = run_command("docker ps")
    if success:
        print(f"   [✓] Docker daemon actif")
    else:
        print(f"   [✗] Docker daemon non accessible")
        print(f"       Assurez-vous que Docker Desktop est démarré")
        return False
    
    return True

def check_python():
    """Vérifie si Python est installé."""
    print("\n" + "="*60)
    print("2. VÉRIFICATION DE PYTHON")
    print("="*60)
    
    # Python version
    python_cmd = "python3" if sys.platform != 'win32' else "python"
    success, stdout, stderr = run_command(f"{python_cmd} --version")
    if success:
        version = stdout.strip() if stdout else "Version inconnue"
        print(f"   [✓] Python installé: {version}")
        
        # Vérifier version 3.9+
        try:
            version_num = version.split()[1]
            major, minor = map(int, version_num.split('.')[:2])
            if major >= 3 and minor >= 9:
                print(f"   [✓] Version compatible (>= 3.9)")
            else:
                print(f"   [✗] Version non compatible (requis: >= 3.9)")
                return False
        except:
            print(f"   [⚠] Impossible de déterminer la version exacte")
    else:
        print(f"   [✗] Python non trouvé")
        print(f"       Installation: https://www.python.org/downloads/")
        return False
    
    # Vérifier pip
    pip_cmd = "pip3" if sys.platform != 'win32' else "pip"
    success, stdout, stderr = run_command(f"{pip_cmd} --version")
    if success:
        print(f"   [✓] pip installé")
    else:
        print(f"   [⚠] pip non trouvé (sera installé automatiquement)")
    
    return True

def check_kubectl():
    """Vérifie si kubectl est installé."""
    print("\n" + "="*60)
    print("3. VÉRIFICATION DE KUBECTL")
    print("="*60)
    
    success, stdout, stderr = run_command("kubectl version --client")
    if success:
        version_line = stdout.split('\n')[0] if stdout else "Version inconnue"
        print(f"   [✓] kubectl installé: {version_line}")
    else:
        print(f"   [✗] kubectl non trouvé")
        print(f"       Installation Windows: choco install kubernetes-cli")
        print(f"       Ou: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/")
        return False
    
    return True

def check_minikube():
    """Vérifie si Minikube est installé et démarré."""
    print("\n" + "="*60)
    print("4. VÉRIFICATION DE MINIKUBE")
    print("="*60)
    
    # Vérifier si Minikube est installé
    success, stdout, stderr = run_command("minikube version")
    if success:
        version = stdout.split('\n')[0] if stdout else "Version inconnue"
        print(f"   [✓] Minikube installé: {version}")
    else:
        # Vérifier via kubectl si c'est Minikube
        success_kubectl, stdout_kubectl, _ = run_command("kubectl get nodes -o jsonpath='{.items[0].metadata.name}'")
        if success_kubectl and 'minikube' in stdout_kubectl.lower():
            print(f"   [✓] Minikube détecté via kubectl (cluster actif)")
        else:
            print(f"   [⚠] Minikube non installé (optionnel si cluster externe)")
            print(f"       Installation: choco install minikube")
            print(f"       Ou: https://minikube.sigs.k8s.io/docs/start/")
            return None  # Optionnel
    
    # Vérifier si Minikube est démarré (via kubectl)
    success_kubectl, stdout_kubectl, _ = run_command("kubectl cluster-info")
    if success_kubectl:
        print(f"   [✓] Cluster Kubernetes accessible")
        # Vérifier si c'est Minikube
        success_nodes, stdout_nodes, _ = run_command("kubectl get nodes -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || kubectl get nodes")
        if success_nodes and ('minikube' in stdout_nodes.lower() or 'minikube' in str(stdout_nodes)):
            print(f"   [✓] Minikube est démarré et actif")
            return True
        else:
            # Cluster accessible mais peut-être pas Minikube
            print(f"   [✓] Cluster Kubernetes accessible (peut être un autre cluster)")
            return True
    else:
        # Essayer minikube status
        success_status, stdout_status, _ = run_command("minikube status")
        if success_status:
            print(f"   [✓] Minikube est démarré")
            return True
        else:
            print(f"   [⚠] Minikube n'est pas démarré ou cluster non accessible")
            print(f"       Démarrer avec: minikube start")
            return False

def check_dvc():
    """Vérifie si DVC est installé."""
    print("\n" + "="*60)
    print("5. VÉRIFICATION DE DVC")
    print("="*60)
    
    success, stdout, stderr = run_command("dvc --version")
    if success:
        version = stdout.strip() if stdout else "Version inconnue"
        print(f"   [✓] DVC installé: {version}")
        return True
    else:
        print(f"   [⚠] DVC non installé (sera installé automatiquement par le pipeline)")
        return None  # Sera installé automatiquement

def check_files():
    """Vérifie si les fichiers nécessaires existent."""
    print("\n" + "="*60)
    print("6. VÉRIFICATION DES FICHIERS")
    print("="*60)
    
    required_files = [
        "requirements.txt",
        "requirements-inference.txt",
        "configs/config.yaml",
        "docker/Dockerfile",
        "docker/docker-compose.yml",
        ".github/workflows/pipeline.yml",
        "k8s/namespace.yaml",
        "k8s/api-deployment.yaml",
        "k8s/api-service.yaml",
        "scripts/prepare_data.py",
        "scripts/get_latest_model.py",
        "src/training/train.py",
        "src/inference/api.py"
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   [✓] {file_path}")
        else:
            print(f"   [✗] {file_path} - MANQUANT")
            all_ok = False
    
    return all_ok

def check_docker_compose_file():
    """Vérifie le fichier docker-compose.yml."""
    print("\n" + "="*60)
    print("7. VÉRIFICATION DOCKER-COMPOSE")
    print("="*60)
    
    compose_file = Path("docker/docker-compose.yml")
    if not compose_file.exists():
        print(f"   [✗] docker-compose.yml non trouvé")
        return False
    
    print(f"   [✓] docker-compose.yml existe")
    
    # Vérifier si on peut lire le fichier (vérification basique)
    try:
        with open(compose_file, 'r') as f:
            content = f.read()
            if 'mlflow' in content.lower() and 'api' in content.lower():
                print(f"   [✓] docker-compose.yml semble valide (services détectés)")
            else:
                print(f"   [⚠] docker-compose.yml trouvé mais contenu suspect")
    except Exception as e:
        print(f"   [✗] Erreur lors de la lecture: {e}")
        return False
    
    return True

def main():
    """Fonction principale."""
    print("\n" + "="*60)
    print("  VÉRIFICATION DES PRÉREQUIS - PIPELINE MLOPS")
    print("="*60)
    
    results = {}
    
    # Vérifications essentielles
    results['docker'] = check_docker()
    results['python'] = check_python()
    results['kubectl'] = check_kubectl()
    results['minikube'] = check_minikube()  # Optionnel
    results['dvc'] = check_dvc()  # Optionnel
    results['files'] = check_files()
    results['docker_compose'] = check_docker_compose_file()
    
    # Résumé
    print("\n" + "="*60)
    print("  RÉSUMÉ")
    print("="*60)
    
    essential_ok = True
    for key, value in results.items():
        if value is True:
            status = "[✓] OK"
        elif value is None:
            status = "[⚠] Optionnel/Installé automatiquement"
        else:
            status = "[✗] MANQUANT/ERREUR"
            if key in ['docker', 'python', 'kubectl', 'files', 'docker_compose']:
                essential_ok = False
        
        name_map = {
            'docker': 'Docker',
            'python': 'Python 3.9+',
            'kubectl': 'kubectl',
            'minikube': 'Minikube (optionnel)',
            'dvc': 'DVC (optionnel)',
            'files': 'Fichiers nécessaires',
            'docker_compose': 'docker-compose.yml'
        }
        print(f"   {name_map.get(key, key)}: {status}")
    
    print("\n" + "="*60)
    if essential_ok:
        print("  ✓ TOUS LES PRÉREQUIS ESSENTIELS SONT RÉUNIS")
        print("="*60)
        print("\n   Vous pouvez tester le pipeline !")
        print("\n   Prochaines étapes:")
        if results.get('minikube') is not True:
            print("   1. Démarrer Minikube: minikube start")
        print("   2. Lancer le pipeline via GitHub Actions (workflow_dispatch)")
        print("   3. Ou tester localement les composants")
    else:
        print("  ✗ CERTAINS PRÉREQUIS SONT MANQUANTS")
        print("="*60)
        print("\n   Veuillez installer les composants manquants avant de continuer.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

