# dagster_fortress/assets/ingestion_assets.py
"""
Ingestion assets for Sovereign Data Fortress

Assets that extract data from external APIs
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from dagster import (
    asset,
    AssetExecutionContext,
    MetadataValue,
    Output
)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ingestion.connectors.crypto_api import CryptoAPIConnector
from dagster_fortress.resources.minio_resource import MinIOResource

@asset(
    name="raw_crypto_prices",
    description="""
    Raw cryptocurrency prices from CoinGecko API.
    
    This asset extracts current price data for major cryptocurrencies
    and stores it in MinIO as Parquet format.
    
    Update frequency: Hourly
    Source: CoinGecko API
    """,
    group_name="ingestion",
    compute_kind="python"
)
def raw_crypto_prices(
    context: AssetExecutionContext,
    minio: MinIOResource
) -> Output[pd.DataFrame]:
    """
    Extract crypto prices from CoinGecko API
    
    Returns:
        DataFrame with crypto price data
    """
    
    context.log.info("🚀 Starting crypto price extraction...")
    
    # Initialize API connector
    symbols = ['bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot']
    connector = CryptoAPIConnector(symbols=symbols)
    
    # Check connection
    status = connector.check_connection()
    if status['status'] != 'success':
        raise Exception(f"API connection failed: {status['message']}")
    
    context.log.info(f"✅ Connected to CoinGecko API")
    
    # Extract data
    records = connector.read_records()
    
    if not records:
        raise Exception("No records extracted from API")
    
    context.log.info(f"📥 Extracted {len(records)} records")
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Add extraction timestamp
    df['_dagster_extracted_at'] = datetime.now()
    
    # Save to MinIO
    minio_client = minio.get_client()
    minio.ensure_bucket('raw-data')
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crypto_prices/{timestamp}.parquet"
    local_path = f"/tmp/crypto_prices_{timestamp}.parquet"
    
    # Write Parquet locally
    df.to_parquet(local_path, index=False, compression='snappy')
    
    # Upload to MinIO
    minio_client.fput_object(
        'raw-data',
        filename,
        local_path
    )
    
    # Cleanup
    import os
    os.remove(local_path)
    
    context.log.info(f"📦 Saved to MinIO: s3://raw-data/{filename}")
    
    # Return with metadata
    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "num_cryptos": df['symbol'].nunique(),
            "symbols": MetadataValue.text(", ".join(df['symbol'].unique())),
            "minio_path": MetadataValue.text(f"s3://raw-data/{filename}"),
            "extraction_time": MetadataValue.text(datetime.now().isoformat()),
            "preview": MetadataValue.md(df.head(3).to_markdown())
        }
    )

@asset(
    name="crypto_price_summary",
    description="Summary statistics of extracted crypto prices",
    group_name="ingestion",
    compute_kind="python",
    deps=["raw_crypto_prices"]  # Depends on raw_crypto_prices
)
def crypto_price_summary(
    context: AssetExecutionContext,
    raw_crypto_prices: pd.DataFrame
) -> Output[dict]:
    """
    Generate summary statistics from raw crypto prices
    
    Args:
        raw_crypto_prices: DataFrame from raw_crypto_prices asset
    
    Returns:
        Dictionary with summary statistics
    """
    
    context.log.info("📊 Generating price summary...")
    
    summary = {
        "total_cryptos": len(raw_crypto_prices),
        "avg_price": float(raw_crypto_prices['current_price'].mean()),
        "total_market_cap": float(raw_crypto_prices['market_cap'].sum()),
        "highest_price": {
            "symbol": raw_crypto_prices.loc[
                raw_crypto_prices['current_price'].idxmax(), 'symbol'
            ],
            "price": float(raw_crypto_prices['current_price'].max())
        },
        "highest_volume": {
            "symbol": raw_crypto_prices.loc[
                raw_crypto_prices['total_volume'].idxmax(), 'symbol'
            ],
            "volume": float(raw_crypto_prices['total_volume'].max())
        }
    }
    
    context.log.info(f"✅ Summary generated for {summary['total_cryptos']} cryptos")
    
    return Output(
        value=summary,
        metadata={
            "total_cryptos": summary['total_cryptos'],
            "avg_price": MetadataValue.float(summary['avg_price']),
            "total_market_cap": MetadataValue.float(summary['total_market_cap']),
            "highest_price_crypto": MetadataValue.text(
                f"{summary['highest_price']['symbol']}: ${summary['highest_price']['price']:,.2f}"
            ),
            "summary_json": MetadataValue.json(summary)
        }
    )
