# dagster_fortress/__init__.py
from dagster import (
    Definitions,
    load_assets_from_modules,
    define_asset_job,
    AssetSelection
)
from pathlib import Path

from dagster_fortress.assets import ingestion_assets, dbt_assets
from dagster_fortress.schedules import daily_schedules, partitioned_schedules
# Removed: test_schedules (file doesn't exist)
from dagster_fortress.sensors import (
    file_sensors,
    status_sensors,
    asset_sensors,
    custom_sensors
)
from dagster_fortress.resources.minio_resource import MinIOResource
from dagster_dbt import DbtCliResource

# Paths
DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt_fortress"
DBT_PROFILES_DIR = Path.home() / ".dbt"

# Assets
ingestion_assets_list = load_assets_from_modules([ingestion_assets])
dbt_assets_list = load_assets_from_modules([dbt_assets])
all_assets = [*ingestion_assets_list, *dbt_assets_list]

# Jobs
full_pipeline_job = define_asset_job(
    name="full_pipeline",
    selection=AssetSelection.all(),
    description="Complete pipeline"
)

# Schedules (without test_schedules)
all_schedules = [
    daily_schedules.daily_crypto_schedule,
    daily_schedules.hourly_crypto_schedule,
    daily_schedules.weekly_refresh_schedule,
    partitioned_schedules.daily_partitioned_schedule
]

# Sensors
all_sensors = [
    file_sensors.new_crypto_file_sensor,
    status_sensors.pipeline_failure_sensor,
    status_sensors.pipeline_success_sensor,
    asset_sensors.when_raw_data_materializes,
    asset_sensors.when_fact_table_updates,
    custom_sensors.business_hours_sensor
]

# Resources
resources = {
    "minio": MinIOResource(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    ),
    "dbt": DbtCliResource(
        project_dir=DBT_PROJECT_DIR,
        profiles_dir=DBT_PROFILES_DIR
    )
}

# Definitions
defs = Definitions(
    assets=all_assets,
    jobs=[full_pipeline_job],
    schedules=all_schedules,
    sensors=all_sensors,
    resources=resources
)
