# dagster_fortress/sensors/status_sensors.py
"""
Run status sensors for monitoring and alerting
"""

from dagster import (
    run_failure_sensor,
    run_status_sensor,
    RunRequest,
    RunFailureSensorContext,
    DagsterRunStatus
)

@run_failure_sensor(
    name="pipeline_failure_alert",
    description="Send alert when pipeline fails"
)
def pipeline_failure_sensor(context: RunFailureSensorContext):
    """
    Alert when any pipeline run fails
    
    In production, this would:
    - Send Slack message
    - Create PagerDuty incident
    - Send email to on-call engineer
    - Log to monitoring system
    """
    
    context.log.error(
        f"🚨 PIPELINE FAILURE DETECTED!\n"
        f"Job: {context.dagster_run.job_name}\n"
        f"Run ID: {context.dagster_run.run_id}\n"
        f"Error: {context.failure_event.message if context.failure_event else 'Unknown'}"
    )
    
    # In production, would send real alerts:
    # send_slack_alert(context)
    # create_pagerduty_incident(context)
    # send_email_alert(context)
    
    # For demo, just log
    print("=" * 60)
    print("🚨 ALERT: Pipeline Failed!")
    print(f"Job: {context.dagster_run.job_name}")
    print(f"Run ID: {context.dagster_run.run_id}")
    print(f"Time: {context.dagster_run.start_time}")
    print("=" * 60)

@run_status_sensor(
    name="pipeline_success_logger",
    run_status=DagsterRunStatus.SUCCESS,
    description="Log successful pipeline completions"
)
def pipeline_success_sensor(context):
    """
    Log when pipelines complete successfully
    
    Useful for:
    - Tracking SLAs
    - Performance monitoring
    - Success metrics
    """
    
    context.log.info(
        f"✅ Pipeline completed successfully!\n"
        f"Job: {context.dagster_run.job_name}\n"
        f"Run ID: {context.dagster_run.run_id}\n"
        f"Duration: {(context.dagster_run.end_time - context.dagster_run.start_time).total_seconds()}s"
    )
    
    # In production:
    # - Update metrics dashboard
    # - Log to analytics
    # - Update SLA tracking
