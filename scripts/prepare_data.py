"""
Script pour préparer et organiser les données du dataset PlantVillage.
- Génère metadata.csv avec les chemins et labels
- Split train/val/test
- Crée la structure de dossiers pour les données préprocessées
"""

import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import yaml


def load_config(config_path="configs/config.yaml"):
    """Charge la configuration depuis le fichier YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def find_image_files(data_dir):
    """Trouve tous les fichiers images dans le répertoire."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_files = []
    
    data_path = Path(data_dir)
    if not data_path.exists():
        raise ValueError(f"Le répertoire {data_dir} n'existe pas")
    
    # Parcourt récursivement tous les dossiers
    for class_dir in data_path.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name
            for image_file in class_dir.iterdir():
                if image_file.suffix in image_extensions:
                    image_files.append({
                        'path': str(image_file),
                        'label': class_name,
                        'class_name': class_name
                    })
    
    return image_files


def create_metadata(data_dir, output_path, config):
    """Crée le fichier metadata.csv avec tous les chemins et labels."""
    print(f"Recherche des images dans {data_dir}...")
    image_files = find_image_files(data_dir)
    
    if len(image_files) == 0:
        raise ValueError(f"Aucune image trouvée dans {data_dir}")
    
    df = pd.DataFrame(image_files)
    
    # Créer un mapping classe -> class_id
    unique_classes = sorted(df['label'].unique())
    class_to_id = {cls: idx for idx, cls in enumerate(unique_classes)}
    df['class_id'] = df['label'].map(class_to_id)
    
    print(f"Trouvé {len(df)} images dans {len(unique_classes)} classes")
    print(f"Classes: {unique_classes[:5]}..." if len(unique_classes) > 5 else f"Classes: {unique_classes}")
    
    # Sauvegarder le metadata
    df.to_csv(output_path, index=False)
    print(f"Metadata sauvegardé dans {output_path}")
    
    # Sauvegarder le mapping classe -> id
    mapping_path = Path(output_path).parent / "class_mapping.yaml"
    with open(mapping_path, 'w') as f:
        yaml.dump({
            'class_to_id': class_to_id,
            'id_to_class': {v: k for k, v in class_to_id.items()},
            'num_classes': len(unique_classes)
        }, f)
    print(f"Mapping des classes sauvegardé dans {mapping_path}")
    
    return df, class_to_id


def split_data(df, config):
    """Divise les données en train/val/test."""
    train_split = config['data']['train_split']
    val_split = config['data']['val_split']
    test_split = config['data']['test_split']
    
    # Stratifié par classe
    train_df, temp_df = train_test_split(
        df,
        test_size=(1 - train_split),
        stratify=df['class_id'],
        random_state=42
    )
    
    # Diviser temp en val et test
    val_size = val_split / (val_split + test_split)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_size),
        stratify=temp_df['class_id'],
        random_state=42
    )
    
    train_df['split'] = 'train'
    val_df['split'] = 'val'
    test_df['split'] = 'test'
    
    print(f"Split réalisé:")
    print(f"  Train: {len(train_df)} images ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Val:   {len(val_df)} images ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test:  {len(test_df)} images ({len(test_df)/len(df)*100:.1f}%)")
    
    return pd.concat([train_df, val_df, test_df], ignore_index=True)


def create_directories(processed_dir):
    """Crée la structure de dossiers pour les données préprocessées."""
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    for split in ['train', 'val', 'test']:
        Path(processed_dir, split).mkdir(parents=True, exist_ok=True)
    print(f"Structure de dossiers créée dans {processed_dir}")


def main():
    """Fonction principale."""
    config = load_config()
    
    data_config = config['data']
    raw_dir = data_config['raw_dir']
    processed_dir = data_config['processed_dir']
    metadata_path = data_config['metadata_path']
    
    # Créer le répertoire pour metadata si nécessaire
    Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Créer metadata.csv
    df, class_mapping = create_metadata(raw_dir, metadata_path, config)
    
    # Split train/val/test
    df_with_split = split_data(df, config)
    df_with_split.to_csv(metadata_path, index=False)
    
    # Créer la structure de dossiers
    create_directories(processed_dir)
    
        # Mettre à jour le nombre de classes dans config si nécessaire
        num_classes = len(class_mapping)
        print(f"\n[SUCCES] Preparation terminee!")
        print(f"   - {len(df_with_split)} images trouvees")
        print(f"   - {num_classes} classes")
        print(f"   - Metadata: {metadata_path}")
        print(f"\n[NOTE] Mettez a jour 'num_classes' dans configs/config.yaml a {num_classes} si different")


if __name__ == "__main__":
    main()


