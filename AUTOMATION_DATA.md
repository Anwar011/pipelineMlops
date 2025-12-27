# Automatisation de la Copie des Données

## 🎯 Solution Automatique

Le workflow GitHub Actions **copie automatiquement les données** si elles n'existent pas dans le workspace du runner.

## ✅ Ce qui est Automatisé

Le workflow inclut maintenant un step **"Copy data if needed"** qui :

1. **Vérifie** si les données existent déjà dans le workspace
2. **Cherche** les données dans plusieurs emplacements possibles :
   - Dans le workspace (si déjà checkout)
   - Dans le repo local (`~/pipelineMlops/`)
   - Dans les chemins relatifs du runner
3. **Copie automatiquement** les données si trouvées
4. **Continue** le workflow même si la copie échoue (avec un avertissement)

## 🔄 Quand est-ce que la Copie se Fait ?

### Première Exécution
- Les données sont **copiées automatiquement** lors du premier workflow

### Exécutions Suivantes
- Si les données existent déjà dans le workspace → **Pas de copie** (rapide)
- Si les données ont été supprimées → **Copie automatique**

### Après dvc add / Mise à Jour
- Si vous faites `dvc add data/raw` avec de nouvelles données
- Les données seront copiées automatiquement lors du prochain workflow

## 📝 Faut-il Copier Manuellement ?

**Non, ce n'est plus nécessaire !** 

Le workflow gère automatiquement la copie. Vous n'avez rien à faire.

## ⚙️ Comment Ça Marche ?

Le script `scripts/copy_data_if_needed.py` :
- S'exécute automatiquement dans le workflow
- Vérifie intelligemment plusieurs emplacements
- Copie seulement si nécessaire
- Ne bloque pas le workflow en cas d'échec (avertissement seulement)

## 🚀 Alternative : Storage Distant (Recommandé pour Production)

Pour une solution plus robuste à long terme, configurez un **storage distant DVC** :

```bash
# Exemple avec S3
dvc remote modify storage url s3://votre-bucket/dvc-storage
dvc push
```

Avec un storage distant :
- ✅ Pas besoin de copier manuellement
- ✅ Les données sont versionnées dans le cloud
- ✅ Accessible depuis n'importe quel runner
- ✅ Plus robuste et scalable

## 📊 Comparaison

| Méthode | Copie Manuelle | Automatique (Actuel) | Storage Distant |
|---------|----------------|----------------------|-----------------|
| Setup initial | ✅ Manuel | ✅ Auto | ✅ Config DVC |
| Maintenance | ❌ À chaque fois | ✅ Auto | ✅ Auto |
| Robustesse | ⚠️ Moyenne | ✅ Bonne | ✅ Excellente |
| Scalabilité | ❌ Limitée | ⚠️ Limitée | ✅ Excellente |

## ✅ Conclusion

**Avec l'automatisation actuelle :**
- ✅ Vous n'avez **rien à faire manuellement**
- ✅ Le workflow copie les données automatiquement
- ✅ Fonctionne pour un self-hosted runner local

**Pour la production :**
- 💡 Considérez un storage distant DVC (S3, Azure, GCS)

