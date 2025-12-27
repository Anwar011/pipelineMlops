#!/bin/bash
# Script Bash pour copier les données vers le runner GitHub Actions
# Utilisation: bash scripts/copy_data_to_runner.sh

# Chemin du runner (ajustez selon votre configuration)
RUNNER_PATH="$HOME/actions-runner/_work/pipelineMlops/pipelineMlops"
SOURCE_DATA_PATH="data/raw/PlantVillage"
TARGET_DATA_PATH="$RUNNER_PATH/data/raw/PlantVillage"

echo ""
echo "================================================================="
echo "  COPIE DES DONNEES VERS LE RUNNER"
echo "================================================================="
echo ""

# Vérifier que les données source existent
if [ ! -d "$SOURCE_DATA_PATH" ]; then
    echo "[ERREUR] Les donnees source n'existent pas: $SOURCE_DATA_PATH"
    echo "Veuillez d'abord telecharger les donnees ou faire dvc pull"
    exit 1
fi

echo "[OK] Donnees source trouvees: $SOURCE_DATA_PATH"

# Créer le répertoire de destination
mkdir -p "$(dirname "$TARGET_DATA_PATH")"

# Copier les données
echo "[INFO] Copie des donnees vers: $TARGET_DATA_PATH"
echo "  Cela peut prendre quelques minutes..."

if cp -r "$SOURCE_DATA_PATH" "$TARGET_DATA_PATH"; then
    echo "[OK] Donnees copiees avec succes!"
    echo ""
    echo "Les donnees sont maintenant disponibles sur le runner."
    echo "Vous pouvez maintenant lancer le workflow GitHub Actions."
else
    echo "[ERREUR] Erreur lors de la copie"
    exit 1
fi

