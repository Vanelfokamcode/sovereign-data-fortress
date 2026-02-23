# dagster_fortress/sensors/file_sensors.py
"""
File-based sensors for event-driven pipeline execution
"""

from dagster import (
    sensor,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    SensorResult
)
from dagster_fortress.resources.minio_resource import MinIOResource
from datetime import datetime

@sensor(
    name="new_crypto_file_sensor",
    job_name="full_pipeline",
    minimum_interval_seconds=60,  # Check every minute
    description="Triggers pipeline when new crypto data file appears in MinIO"
)
def new_crypto_file_sensor(context: SensorEvaluationContext):
    """
    Monitor MinIO for new crypto price files
    
    When a new file is detected:
    - Trigger full pipeline
    - Tag with file info
    - Track file in cursor
    
    This enables real-time data processing instead of scheduled batches
    """
    
    # Get MinIO client (hardcoded for simplicity, could use resource)
    from minio import Minio
    
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )
    
    bucket = "raw-data"
    prefix = "crypto_prices/"
    
    # Get cursor (last processed file)
    last_processed = context.cursor or None
    
    try:
        # List all files
        objects = list(client.list_objects(bucket, prefix=prefix))
        
        if not objects:
            return SkipReason("No files found in MinIO")
        
        # Get latest file
        latest_file = max(objects, key=lambda x: x.last_modified)
        latest_file_name = latest_file.object_name
        
        # Check if this is a new file
        if last_processed == latest_file_name:
            return SkipReason(f"No new files (latest: {latest_file_name})")
        
        # New file detected!
        context.log.info(f"🚀 New file detected: {latest_file_name}")
        
        return SensorResult(
            run_requests=[
                RunRequest(
                    run_key=f"sensor_run_{latest_file_name}",
                    tags={
                        "trigger": "file_sensor",
                        "file": latest_file_name,
                        "detected_at": datetime.now().isoformat()
                    }
                )
            ],
            cursor=latest_file_name  # Update cursor
        )
        
    except Exception as e:
        context.log.error(f"Error checking MinIO: {e}")
        return SkipReason(f"Error: {e}")
