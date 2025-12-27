# Script PowerShell pour copier les données vers le runner GitHub Actions
# Utilisation: .\scripts\copy_data_to_runner.ps1

$ErrorActionPreference = "Stop"

# Chemin du runner (ajustez selon votre configuration)
$runnerPath = "$env:USERPROFILE\actions-runner\_work\pipelineMlops\pipelineMlops"
$sourceDataPath = "data\raw\PlantVillage"
$targetDataPath = Join-Path $runnerPath "data\raw\PlantVillage"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  COPIE DES DONNEES VERS LE RUNNER" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que les données source existent
if (-not (Test-Path $sourceDataPath)) {
    Write-Host "[ERREUR] Les donnees source n'existent pas: $sourceDataPath" -ForegroundColor Red
    Write-Host "Veuillez d'abord telecharger les donnees ou faire dvc pull" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Donnees source trouvees: $sourceDataPath" -ForegroundColor Green

# Créer le répertoire de destination
$targetParentDir = Split-Path $targetDataPath -Parent
if (-not (Test-Path $targetParentDir)) {
    Write-Host "[INFO] Creation du repertoire: $targetParentDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $targetParentDir | Out-Null
}

# Copier les données
Write-Host "[INFO] Copie des donnees vers: $targetDataPath" -ForegroundColor Yellow
Write-Host "  Cela peut prendre quelques minutes..." -ForegroundColor Yellow

try {
    Copy-Item -Path $sourceDataPath -Destination $targetDataPath -Recurse -Force
    Write-Host "[OK] Donnees copiees avec succes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Les donnees sont maintenant disponibles sur le runner." -ForegroundColor Green
    Write-Host "Vous pouvez maintenant lancer le workflow GitHub Actions." -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Erreur lors de la copie: $_" -ForegroundColor Red
    exit 1
}

