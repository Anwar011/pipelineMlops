"""
Métriques Prometheus pour l'API de prédiction.
"""

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Compteurs
prediction_requests_total = Counter(
    'prediction_requests_total',
    'Total number of prediction requests',
    ['status']
)

prediction_errors_total = Counter(
    'prediction_errors_total',
    'Total number of prediction errors',
    ['error_type']
)

# Histogrammes
prediction_duration_seconds = Histogram(
    'prediction_duration_seconds',
    'Prediction processing time in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

prediction_confidence = Histogram(
    'prediction_confidence',
    'Prediction confidence scores',
    buckets=[0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

# Gauges
model_loaded = Gauge(
    'model_loaded',
    'Whether the model is loaded (1) or not (0)'
)

model_classes_total = Gauge(
    'model_classes_total',
    'Total number of classes in the model'
)


