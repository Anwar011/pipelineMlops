# Guide: Copier les Données sur le Runner GitHub Actions

## 📋 Vue d'ensemble

Pour qu'un **self-hosted runner** puisse utiliser les données, il faut les copier sur le runner. Ce guide explique comment faire.

## 🔍 Localisation du Runner

Le runner GitHub Actions stocke le code dans :
```
C:\Users\<votre-utilisateur>\actions-runner\_work\<repo>\<repo>
```

Pour ce projet :
```
C:\Users\elmou\actions-runner\_work\pipelineMlops\pipelineMlops
```

## 📁 Données à Copier

Vous devez copier :
- `data/raw/PlantVillage/` → Le dossier complet avec toutes les images

**Ou** le storage DVC :
- `.dvc/storage/` → Le cache DVC (si vous voulez que DVC fonctionne)

## 🚀 Méthodes

### Méthode 1: Script PowerShell (Windows - Recommandé)

```powershell
# Exécuter le script
.\scripts\copy_data_to_runner.ps1
```

Le script va :
1. Vérifier que les données source existent
2. Créer le répertoire de destination si nécessaire
3. Copier les données vers le runner

### Méthode 2: Script Bash (Linux/WSL/Git Bash)

```bash
bash scripts/copy_data_to_runner.sh
```

### Méthode 3: Copie Manuelle

**Avec PowerShell :**
```powershell
# Créer le répertoire de destination
$runnerPath = "$env:USERPROFILE\actions-runner\_work\pipelineMlops\pipelineMlops"
New-Item -ItemType Directory -Force -Path "$runnerPath\data\raw"

# Copier les données
Copy-Item -Path "data\raw\PlantVillage" -Destination "$runnerPath\data\raw\PlantVillage" -Recurse -Force
```

**Avec Git Bash ou WSL :**
```bash
RUNNER_PATH="$HOME/actions-runner/_work/pipelineMlops/pipelineMlops"
mkdir -p "$RUNNER_PATH/data/raw"
cp -r data/raw/PlantVillage "$RUNNER_PATH/data/raw/PlantVillage"
```

### Méthode 4: Copie du Storage DVC (Alternative)

Si vous préférez copier le storage DVC :

```powershell
$runnerPath = "$env:USERPROFILE\actions-runner\_work\pipelineMlops\pipelineMlops"
Copy-Item -Path ".dvc\storage" -Destination "$runnerPath\.dvc\storage" -Recurse -Force
```

Puis dans le workflow, `dvc pull` récupérera les données depuis ce storage.

## ⚠️ Important

1. **Avant le premier workflow** : Exécutez le script de copie pour que les données soient disponibles
2. **Taille des données** : La copie peut prendre du temps (les données font ~650MB)
3. **Vérification** : Après la copie, vérifiez que `data/raw/PlantVillage` existe sur le runner

## ✅ Vérification

Pour vérifier que les données sont bien copiées :

```powershell
$runnerPath = "$env:USERPROFILE\actions-runner\_work\pipelineMlops\pipelineMlops"
Test-Path "$runnerPath\data\raw\PlantVillage"
# Doit retourner True
```

## 🔄 Quand Copier ?

- **Première fois** : Avant le premier workflow
- **Après mise à jour des données** : Si vous ajoutez/modifiez des données et faites `dvc add`, copiez à nouveau
- **Automatisation possible** : Vous pouvez créer un script qui copie automatiquement après chaque `dvc add`

## 🎯 Alternative: Storage Distant

Si vous ne voulez pas copier manuellement, configurez DVC pour utiliser un storage distant (S3, Azure Blob, etc.) :

```bash
# Exemple avec S3
dvc remote modify storage --local url s3://votre-bucket/dvc-storage
dvc push
```

Le runner pourra alors utiliser `dvc pull` pour récupérer les données depuis le storage distant.

