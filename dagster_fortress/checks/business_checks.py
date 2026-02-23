# dagster_fortress/checks/business_checks.py
"""
Business logic asset checks
"""

from dagster import (
    asset_check,
    AssetCheckResult,
    AssetCheckSeverity,
    AssetKey
)
import pandas as pd
from datetime import datetime, timedelta

@asset_check(
    asset=AssetKey("raw_crypto_prices"),
    name="data_is_fresh",
    description="Data should be less than 2 hours old"
)
def check_data_freshness(raw_crypto_prices: pd.DataFrame) -> AssetCheckResult:
    """
    Freshness check: Data should be recent
    
    SLA: Data must be < 2 hours old
    """
    
    if '_dagster_extracted_at' not in raw_crypto_prices.columns:
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.WARN,
            metadata={
                "message": "Cannot determine freshness (missing timestamp)"
            }
        )
    
    latest_extraction = pd.to_datetime(
        raw_crypto_prices['_dagster_extracted_at']
    ).max()
    
    now = datetime.now()
    age_hours = (now - latest_extraction).total_seconds() / 3600
    
    if age_hours > 2:
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.WARN,
            metadata={
                "age_hours": round(age_hours, 2),
                "sla_hours": 2,
                "latest_extraction": latest_extraction.isoformat()
            }
        )
    
    return AssetCheckResult(
        passed=True,
        metadata={
            "age_hours": round(age_hours, 2),
            "latest_extraction": latest_extraction.isoformat(),
            "status": "Fresh ✅"
        }
    )

@asset_check(
    asset=AssetKey("raw_crypto_prices"),
    name="market_cap_consistency",
    description="Market cap should correlate with volume"
)
def check_market_cap_volume_ratio(raw_crypto_prices: pd.DataFrame) -> AssetCheckResult:
    """
    Business logic check: Market cap and volume should be correlated
    
    Very small market cap + huge volume = suspicious
    """
    
    df = raw_crypto_prices.copy()
    
    # Calculate ratio (volume / market_cap)
    df['ratio'] = df['total_volume'] / df['market_cap']
    
    # Flag suspicious ratios (> 0.5 means volume > 50% of market cap)
    suspicious = df[df['ratio'] > 0.5]
    
    if len(suspicious) > 0:
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.WARN,
            metadata={
                "suspicious_count": len(suspicious),
                "symbols": ", ".join(suspicious['symbol'].tolist()),
                "message": "Unusually high volume/market_cap ratio detected"
            }
        )
    
    return AssetCheckResult(
        passed=True,
        metadata={
            "max_ratio": float(df['ratio'].max()),
            "message": "Volume/market_cap ratios look normal"
        }
    )
