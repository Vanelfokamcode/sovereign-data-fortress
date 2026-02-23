# monitoring/exporters/dagster_metrics_exporter.py
"""
Custom Prometheus exporter for Dagster metrics

Exposes Dagster pipeline metrics in Prometheus format
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import random

# Define metrics
pipeline_runs_total = Counter(
    'dagster_pipeline_runs_total',
    'Total number of pipeline runs',
    ['pipeline', 'status']
)

pipeline_duration_seconds = Histogram(
    'dagster_pipeline_duration_seconds',
    'Pipeline execution duration in seconds',
    ['pipeline'],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
)

asset_materializations_total = Counter(
    'dagster_asset_materializations_total',
    'Total asset materializations',
    ['asset_name', 'asset_group']
)

asset_rows_processed = Gauge(
    'dagster_asset_rows_processed',
    'Number of rows processed by asset',
    ['asset_name']
)

data_quality_score = Gauge(
    'dagster_data_quality_score',
    'Data quality score (0-100)',
    ['pipeline']
)

pipeline_lag_seconds = Gauge(
    'dagster_pipeline_lag_seconds',
    'Time since last successful run',
    ['pipeline']
)

def collect_metrics():
    """
    Collect metrics from Dagster
    
    In production, this would query Dagster GraphQL API
    or read from Dagster database
    """
    
    # Simulated metrics (in production, fetch from Dagster)
    pipeline_runs_total.labels(
        pipeline='full_pipeline',
        status='success'
    ).inc()
    
    pipeline_duration_seconds.labels(
        pipeline='full_pipeline'
    ).observe(random.uniform(60, 180))
    
    asset_materializations_total.labels(
        asset_name='raw_crypto_prices',
        asset_group='ingestion'
    ).inc()
    
    asset_rows_processed.labels(
        asset_name='raw_crypto_prices'
    ).set(random.randint(3, 10))
    
    data_quality_score.labels(
        pipeline='full_pipeline'
    ).set(random.uniform(95, 100))
    
    pipeline_lag_seconds.labels(
        pipeline='full_pipeline'
    ).set(random.uniform(0, 3600))

if __name__ == '__main__':
    # Start Prometheus HTTP server
    start_http_server(8000)
    print("🔥 Dagster metrics exporter started on port 8000")
    print("📊 Metrics available at http://localhost:8000/metrics")
    
    # Collect metrics periodically
    while True:
        collect_metrics()
        time.sleep(15)  # Update every 15 seconds
