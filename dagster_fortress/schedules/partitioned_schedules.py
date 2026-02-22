# dagster_fortress/schedules/partitioned_schedules.py
"""
Partitioned schedules for time-based data processing
"""

from dagster import (
    schedule,
    RunRequest,
    ScheduleEvaluationContext,
    DailyPartitionsDefinition,
    build_schedule_from_partitioned_job,
    define_asset_job,
    AssetSelection
)
from datetime import datetime, timedelta

# Define daily partitions (for historical processing)
daily_partitions = DailyPartitionsDefinition(
    start_date="2024-01-01",
    timezone="Europe/Paris"
)

# Partitioned job (processes one day at a time)
# Note: This would need partitioned assets, simplified for demo
@schedule(
    name="daily_partitioned_ingestion",
    cron_schedule="0 7 * * *",  # 7 AM daily
    job_name="full_pipeline",
    description="Process yesterday's data partition"
)
def daily_partitioned_schedule(context: ScheduleEvaluationContext):
    """
    Process data for yesterday (one partition per day)
    
    This allows:
    - Backfilling historical dates
    - Reprocessing specific days
    - Incremental processing
    """
    
    # Get yesterday's date
    execution_date = context.scheduled_execution_time.date() - timedelta(days=1)
    
    return RunRequest(
        run_key=f"partition_{execution_date.strftime('%Y%m%d')}",
        tags={
            "schedule": "partitioned",
            "partition_date": execution_date.strftime("%Y-%m-%d")
        }
    )
