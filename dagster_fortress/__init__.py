# dagster_fortress/__init__.py
"""
Sovereign Data Fortress - Dagster Definitions

Main entry point for Dagster workspace
"""

from dagster import (
    Definitions,
    load_assets_from_modules,
    define_asset_job
)

from dagster_fortress.assets import ingestion_assets
from dagster_fortress.resources.minio_resource import MinIOResource

# Load all assets
all_assets = load_assets_from_modules([ingestion_assets])

# Define jobs
ingestion_job = define_asset_job(
    name="ingestion_job",
    selection=["raw_crypto_prices", "crypto_price_summary"],
    description="Extract crypto prices from API and generate summary"
)

# Define resources
resources = {
    "minio": MinIOResource(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )
}

# Main definitions
defs = Definitions(
    assets=all_assets,
    jobs=[ingestion_job],
    resources=resources
)
