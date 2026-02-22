# dagster_fortress/assets/dbt_assets.py
"""
dbt assets for Dagster
"""

from pathlib import Path
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

# Path to dbt manifest
DBT_MANIFEST_PATH = Path(__file__).parent.parent.parent / "dbt_fortress" / "target" / "manifest.json"

@dbt_assets(
    manifest=DBT_MANIFEST_PATH,
    name="dbt_fortress_models"
)
def dbt_fortress_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    All dbt models as Dagster assets
    """
    yield from dbt.cli(["build"], context=context).stream()
