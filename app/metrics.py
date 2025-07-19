from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
from flask import request

# Initialize Prometheus metrics
metrics = PrometheusMetrics.for_app_factory()

# Create a counter for rate limit breaches
rate_limit_counter = Counter(
    'flask_rate_limit_total',
    'Total number of times the rate limit was reached',
    ['endpoint']
)