"""
Script pour vérifier que le modèle est bien dans MLflow.
Utilisé dans le workflow GitHub Actions.
"""

import sys
import mlflow

try:
    mlflow.set_tracking_uri('http://localhost:5000')
    client = mlflow.tracking.MlflowClient()
    
    exp = client.get_experiment_by_name('plant_disease_mvp')
    if not exp:
        print('[ERREUR] Expérience non trouvée')
        sys.exit(1)
    
    runs = client.search_runs(
        [exp.experiment_id],
        order_by=['start_time DESC'],
        max_results=1
    )
    
    if not runs:
        print('[ERREUR] Aucun run trouvé')
        sys.exit(1)
    
    run_id = runs[0].info.run_id
    print(f'[OK] Run trouvé: {run_id}')
    
    artifacts = client.list_artifacts(run_id, 'model')
    if artifacts:
        print('[OK] Modèle trouvé dans MLflow')
        sys.exit(0)
    else:
        print('[ERREUR] Modèle non trouvé dans MLflow')
        sys.exit(1)

except Exception as e:
    print(f'[ERREUR] {e}')
    sys.exit(1)

