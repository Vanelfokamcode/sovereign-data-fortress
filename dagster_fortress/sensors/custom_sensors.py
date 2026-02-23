# dagster_fortress/sensors/custom_sensors.py
"""
Custom sensors with complex logic
"""

from dagster import (
    sensor,
    RunRequest,
    SensorEvaluationContext,
    SkipReason
)
from datetime import datetime, time

@sensor(
    name="business_hours_only_sensor",
    job_name="full_pipeline",
    minimum_interval_seconds=300,  # Check every 5 minutes
    description="Only trigger during business hours (9 AM - 6 PM weekdays)"
)
def business_hours_sensor(context: SensorEvaluationContext):
    """
    Custom sensor that only triggers during business hours
    
    Rules:
    - Monday-Friday only
    - 9 AM - 6 PM only
    - No runs on weekends or nights
    
    Use case: Cost optimization, avoid disrupting production during peak hours
    """
    
    now = datetime.now()
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return SkipReason("Weekend - sensor inactive")
    
    # Check if business hours
    business_start = time(9, 0)  # 9 AM
    business_end = time(18, 0)   # 6 PM
    current_time = now.time()
    
    if not (business_start <= current_time <= business_end):
        return SkipReason(f"Outside business hours (current: {current_time.strftime('%H:%M')})")
    
    # Check if we've already run today
    last_run_date = context.cursor
    today = now.strftime("%Y-%m-%d")
    
    if last_run_date == today:
        return SkipReason(f"Already ran today ({today})")
    
    # All conditions met - trigger run
    context.log.info(f"✅ Business hours check passed - triggering pipeline")
    
    return RunRequest(
        run_key=f"business_hours_{today}",
        run_config={},
        tags={
            "trigger": "business_hours_sensor",
            "date": today,
            "time": now.strftime("%H:%M")
        }
    )
