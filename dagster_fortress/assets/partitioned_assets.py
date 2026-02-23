# dagster_fortress/assets/partitioned_assets.py
"""
Partitioned assets for historical data processing and backfills
"""

from dagster import (
    asset,
    AssetExecutionContext,
    DailyPartitionsDefinition,
    Output,
    MetadataValue
)
from datetime import datetime, timedelta
import pandas as pd

# Define daily partitions starting from Jan 1, 2024
daily_partitions = DailyPartitionsDefinition(
    start_date="2024-01-01",
    timezone="Europe/Paris"
)

@asset(
    name="daily_crypto_snapshot",
    description="""
    Daily partitioned crypto price snapshots.
    
    Partitions enable:
    - Processing one day at a time
    - Backfilling historical dates
    - Reprocessing specific days
    - Incremental processing
    """,
    partitions_def=daily_partitions,
    group_name="partitioned"
)
def daily_crypto_snapshot(context: AssetExecutionContext) -> Output[pd.DataFrame]:
    """
    Create a snapshot of crypto prices for a specific date partition
    
    Partition key format: YYYY-MM-DD (e.g., "2024-02-23")
    """
    
    # Get the partition date
    partition_date_str = context.partition_key
    partition_date = datetime.strptime(partition_date_str, "%Y-%m-%d")
    
    context.log.info(f"📅 Processing partition: {partition_date_str}")
    
    # Simulate fetching data for this specific date
    # In production, this would query historical data
    data = {
        'date': [partition_date] * 5,
        'symbol': ['BTC', 'ETH', 'SOL', 'ADA', 'DOT'],
        'price': [42000, 2500, 100, 0.50, 7.5],
        'partition_key': [partition_date_str] * 5
    }
    
    df = pd.DataFrame(data)
    
    context.log.info(f"✅ Processed {len(df)} records for {partition_date_str}")
    
    return Output(
        value=df,
        metadata={
            "partition_date": partition_date_str,
            "num_records": len(df),
            "date_range": MetadataValue.text(f"{partition_date_str} to {partition_date_str}"),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
    )

@asset(
    name="weekly_crypto_summary",
    description="Weekly aggregated crypto metrics (depends on daily snapshots)",
    partitions_def=daily_partitions,
    group_name="partitioned",
    deps=["daily_crypto_snapshot"]
)
def weekly_crypto_summary(
    context: AssetExecutionContext,
    daily_crypto_snapshot: pd.DataFrame
) -> Output[dict]:
    """
    Aggregate daily snapshots into weekly summaries
    
    Demonstrates partition dependencies and aggregation
    """
    
    partition_date_str = context.partition_key
    
    context.log.info(f"📊 Generating weekly summary for week including {partition_date_str}")
    
    summary = {
        "partition_date": partition_date_str,
        "avg_price": float(daily_crypto_snapshot['price'].mean()),
        "total_cryptos": len(daily_crypto_snapshot),
        "generated_at": datetime.now().isoformat()
    }
    
    return Output(
        value=summary,
        metadata={
            "partition_date": partition_date_str,
            "avg_price": MetadataValue.float(summary['avg_price']),
            "summary": MetadataValue.json(summary)
        }
    )
