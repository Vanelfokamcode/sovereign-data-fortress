# dagster_fortress/sensors/asset_sensors.py
"""
Asset-based sensors for dependency-driven execution
"""

from dagster import (
    asset_sensor,
    RunRequest,
    SensorEvaluationContext,
    AssetKey,
    EventLogEntry
)

@asset_sensor(
    asset_key=AssetKey("raw_crypto_prices"),
    name="downstream_on_new_data",
    job_name="full_pipeline",
    description="Trigger downstream processing when raw data updates"
)
def when_raw_data_materializes(context: SensorEvaluationContext, asset_event: EventLogEntry):
    """
    Trigger full pipeline when raw_crypto_prices is materialized
    
    Use case:
    - Manual materialization of raw_crypto_prices
    - Automatically trigger all downstream transformations
    - Keep everything in sync
    """
    
    context.log.info(
        f"🔔 raw_crypto_prices updated!\n"
        f"Materialization ID: {asset_event.dagster_event.event_specific_data.materialization.metadata}\n"
        f"Triggering downstream processing..."
    )
    
    return RunRequest(
        run_key=f"asset_triggered_{asset_event.dagster_event.event_specific_data.materialization.label}",
        tags={
            "trigger": "asset_sensor",
            "upstream_asset": "raw_crypto_prices",
            "materialization_id": str(asset_event.run_id)
        }
    )

@asset_sensor(
    asset_key=AssetKey(["dbt_fortress_models", "fct_daily_crypto_prices"]),
    name="alert_on_marts_update",
    description="Alert when fact table is updated"
)
def when_fact_table_updates(context: SensorEvaluationContext, asset_event: EventLogEntry):
    """
    Alert business users when fact table is refreshed
    
    In production:
    - Send Slack message to #data-updates
    - Trigger BI dashboard refresh
    - Update data catalog
    """
    
    context.log.info(
        f"📊 Fact table updated!\n"
        f"Asset: fct_daily_crypto_prices\n"
        f"Downstream systems can now use fresh data"
    )
    
    # In production:
    # - send_slack_notification("#data-updates", "Fact table refreshed")
    # - trigger_tableau_refresh()
    # - update_data_catalog()
    
    # No RunRequest = sensor just logs/alerts, doesn't trigger job
