# dagster_fortress/schedules/daily_schedules.py
"""
Daily schedules for automated pipeline execution
"""

from dagster import (
    schedule,
    RunRequest,
    ScheduleEvaluationContext
)

@schedule(
    name="daily_crypto_ingestion",
    cron_schedule="0 6 * * *",  # Every day at 6 AM
    job_name="full_pipeline",
    description="Daily crypto price ingestion and transformation"
)
def daily_crypto_schedule(context: ScheduleEvaluationContext):
    """
    Run the complete crypto pipeline daily at 6 AM
    
    This schedule:
    - Extracts latest crypto prices from API
    - Loads to MinIO and Postgres
    - Runs dbt transformations
    - Updates all marts
    """
    
    return RunRequest(
        run_key=f"daily_run_{context.scheduled_execution_time.strftime('%Y%m%d')}",
        tags={
            "schedule": "daily",
            "pipeline": "crypto",
            "execution_date": context.scheduled_execution_time.strftime("%Y-%m-%d")
        }
    )

@schedule(
    name="hourly_crypto_ingestion",
    cron_schedule="0 * * * *",  # Every hour at minute 0
    job_name="full_pipeline",
    description="Hourly crypto price updates"
)
def hourly_crypto_schedule(context: ScheduleEvaluationContext):
    """
    Run crypto ingestion every hour
    
    For more frequent price updates
    """
    
    return RunRequest(
        run_key=f"hourly_run_{context.scheduled_execution_time.strftime('%Y%m%d_%H')}",
        tags={
            "schedule": "hourly",
            "pipeline": "crypto",
            "hour": context.scheduled_execution_time.strftime("%H")
        }
    )

@schedule(
    name="weekly_full_refresh",
    cron_schedule="0 0 * * 0",  # Every Sunday at midnight
    job_name="full_pipeline",
    description="Weekly full data refresh"
)
def weekly_refresh_schedule(context: ScheduleEvaluationContext):
    """
    Full pipeline refresh every Sunday
    
    For weekly data quality checks and full rebuilds
    """
    
    return RunRequest(
        run_key=f"weekly_run_{context.scheduled_execution_time.strftime('%Y_week_%U')}",
        tags={
            "schedule": "weekly",
            "pipeline": "crypto",
            "week": context.scheduled_execution_time.strftime("%U")
        }
    )
