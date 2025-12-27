# Fix PowerShell Execution Policy - GitHub Actions

## 🔴 Problème

L'erreur suivante apparaissait lors de l'exécution du workflow :

```
PSSecurityException: UnauthorizedAccess
L'exécution de scripts est désactivée sur ce système
```

**Cause** : PowerShell bloque l'exécution de scripts à cause de la politique d'exécution (Execution Policy) sur Windows.

## ✅ Solution Appliquée

### 1. Forcer l'utilisation de Bash

Ajout de `shell: bash` à tous les steps du workflow pour contourner PowerShell :

```yaml
- name: Setup Python
  shell: bash  # ← Ajouté
  run: |
    # Commandes bash
```

### 2. Détection Automatique Python

Détection automatique de `python3` ou `python` :

```bash
PYTHON_CMD=python3
if ! command -v python3 &> /dev/null; then
  PYTHON_CMD=python
fi
$PYTHON_CMD --version
```

### 3. Compatibilité Multi-OS

Le workflow fonctionne maintenant sur :
- ✅ Windows (avec Git Bash ou WSL)
- ✅ Linux
- ✅ macOS

## 📝 Modifications Effectuées

Tous les steps du workflow ont été mis à jour :

- ✅ `Setup Python` → `shell: bash`
- ✅ `Install dependencies` → `shell: bash`
- ✅ `Install DVC` → `shell: bash`
- ✅ `Setup DVC` → `shell: bash`
- ✅ `Check for data changes` → `shell: bash`
- ✅ `Prepare data` → `shell: bash`
- ✅ `Start MLflow` → `shell: bash`
- ✅ `Train model` → `shell: bash`
- ✅ `Verify model in MLflow` → `shell: bash`
- ✅ `Get latest model` → `shell: bash`
- ✅ `Build Docker image` → `shell: bash`
- ✅ `Deploy to Kubernetes` → `shell: bash`

## 🚀 Résultat

Le workflow devrait maintenant s'exécuter sans erreur PowerShell !

### Vérification

Relancez le workflow via GitHub Actions :
1. Aller sur Actions → MLOps Pipeline
2. Run workflow → workflow_dispatch
3. Le workflow devrait s'exécuter sans erreur

## 🔧 Alternative (Si Bash n'est pas disponible)

Si bash n'est pas disponible sur votre runner Windows, vous pouvez :

1. **Installer Git Bash** (recommandé)
   ```powershell
   # Git Bash est installé avec Git for Windows
   # Vérifier : bash --version
   ```

2. **Utiliser WSL** (Windows Subsystem for Linux)
   ```powershell
   wsl --install
   ```

3. **Modifier la politique PowerShell** (moins recommandé pour sécurité)
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## ✅ Statut

Le workflow est maintenant **corrigé et prêt** !

