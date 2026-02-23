# dagster_fortress/assets/resilient_ingestion_assets.py
"""
Ingestion assets with retry policies for resilience
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from dagster import (
    asset,
    AssetExecutionContext,
    MetadataValue,
    Output,
    RetryPolicy,
    Backoff
)

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ingestion.connectors.crypto_api import CryptoAPIConnector
from dagster_fortress.resources.minio_resource import MinIOResource

@asset(
    name="resilient_raw_crypto_prices",
    description="""
    Raw crypto prices with automatic retry on failure.
    
    Retry policy:
    - Max attempts: 3
    - Delay: Exponential backoff (60s, 120s, 240s)
    """,
    group_name="ingestion",
    compute_kind="python",
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=60,
        backoff=Backoff.EXPONENTIAL
        # Removed jitter - not supported in this Dagster version
    )
)
def resilient_raw_crypto_prices(
    context: AssetExecutionContext,
    minio: MinIOResource
) -> Output[pd.DataFrame]:
    """
    Extract crypto prices with automatic retry on transient failures
    """
    
    context.log.info("🚀 Starting resilient crypto extraction...")
    
    # Initialize connector
    symbols = ['bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot']
    connector = CryptoAPIConnector(symbols=symbols)
    
    # Check connection (may fail and trigger retry)
    status = connector.check_connection()
    if status['status'] != 'success':
        error_msg = f"API connection failed: {status['message']}"
        context.log.error(error_msg)
        raise Exception(error_msg)
    
    context.log.info("✅ Connected to API")
    
    # Extract data (may fail and trigger retry)
    try:
        records = connector.read_records()
        
        if not records:
            raise Exception("No records extracted - will retry")
        
        context.log.info(f"📥 Extracted {len(records)} records")
        
    except Exception as e:
        context.log.error(f"Extraction failed: {e}")
        raise
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    df['_dagster_extracted_at'] = datetime.now()
    
    # Save to MinIO
    try:
        minio_client = minio.get_client()
        minio.ensure_bucket('raw-data')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crypto_prices/{timestamp}.parquet"
        local_path = f"/tmp/crypto_prices_{timestamp}.parquet"
        
        df.to_parquet(local_path, index=False, compression='snappy')
        minio_client.fput_object('raw-data', filename, local_path)
        
        import os
        os.remove(local_path)
        
        context.log.info(f"📦 Saved to MinIO: s3://raw-data/{filename}")
        
    except Exception as e:
        context.log.error(f"MinIO upload failed: {e}")
        raise
    
    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "num_cryptos": df['symbol'].nunique(),
            "symbols": MetadataValue.text(", ".join(df['symbol'].unique())),
            "minio_path": MetadataValue.text(f"s3://raw-data/{filename}"),
            "extraction_time": MetadataValue.text(datetime.now().isoformat())
        }
    )
