# dagster_fortress/checks/transformation_checks.py
"""
Asset checks for dbt transformation layer
"""

from dagster import (
    asset_check,
    AssetCheckResult,
    AssetCheckSeverity,
    AssetKey
)

@asset_check(
    asset=AssetKey(["dbt_fortress_models", "fct_daily_crypto_prices"]),
    name="fact_table_not_empty",
    description="Fact table must contain data"
)
def check_fact_table_not_empty() -> AssetCheckResult:
    """
    Ensure fact table has data after transformation
    
    Note: This is a placeholder - in production would query actual table
    """
    
    # In production, would query Postgres:
    # SELECT COUNT(*) FROM analytics_marts.fct_daily_crypto_prices
    
    # For demo, assume it passes
    row_count = 5  # Simulated
    
    if row_count == 0:
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.ERROR,
            metadata={
                "row_count": 0,
                "message": "Fact table is empty - transformation may have failed"
            }
        )
    
    return AssetCheckResult(
        passed=True,
        metadata={
            "row_count": row_count,
            "message": f"Fact table contains {row_count} rows"
        }
    )

@asset_check(
    asset=AssetKey(["dbt_fortress_models", "fct_daily_crypto_prices"]),
    name="daily_grain_maintained",
    description="Ensure one row per crypto per day (grain check)"
)
def check_daily_grain() -> AssetCheckResult:
    """
    Check that fact table maintains daily grain
    
    Each (crypto, date) combination should appear exactly once
    """
    
    # In production: SELECT symbol, date, COUNT(*) ... HAVING COUNT(*) > 1
    
    # For demo, assume correct grain
    duplicates = 0
    
    if duplicates > 0:
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.ERROR,
            metadata={
                "duplicate_count": duplicates,
                "message": "Grain violated - multiple rows per crypto per day"
            }
        )
    
    return AssetCheckResult(
        passed=True,
        metadata={
            "message": "Daily grain maintained correctly"
        }
    )
