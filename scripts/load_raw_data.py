# scripts/load_raw_data.py
"""
Load raw crypto data from MinIO into Postgres
This simulates what would normally be done by dbt's external tables
"""

import os
import sys
import pandas as pd
import psycopg2
from pathlib import Path
from minio import Minio
from dotenv import load_dotenv
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

def get_postgres_connection():
    """Get Postgres connection"""
    return psycopg2.connect(
        host='localhost',
        port=os.getenv('POSTGRES_PORT', 5433),
        user=os.getenv('POSTGRES_USER', 'dataeng'),
        password=os.getenv('POSTGRES_PASSWORD', 'fortress2024'),
        database=os.getenv('POSTGRES_DB', 'warehouse')
    )

def get_minio_client():
    """Get MinIO client"""
    return Minio(
        f"localhost:{os.getenv('MINIO_API_PORT', '9000')}",
        access_key=os.getenv('MINIO_ROOT_USER', 'minioadmin'),
        secret_key=os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin123'),
        secure=False
    )

def load_latest_from_minio():
    """Load latest Parquet file from MinIO"""
    
    print("📥 Loading data from MinIO...")
    
    minio_client = get_minio_client()
    bucket = "raw-data"
    prefix = "crypto_prices/"
    
    # List all objects
    objects = list(minio_client.list_objects(bucket, prefix=prefix))
    
    if not objects:
        print("❌ No data found in MinIO. Run: make ingest")
        return None
    
    # Get latest file
    latest = max(objects, key=lambda x: x.last_modified)
    print(f"   Latest file: {latest.object_name}")
    
    # Download and read Parquet
    response = minio_client.get_object(bucket, latest.object_name)
    data = response.read()
    
    df = pd.read_parquet(io.BytesIO(data))
    print(f"   ✅ Loaded {len(df)} records")
    
    return df

def create_raw_schema(conn):
    """Create raw schema in Postgres"""
    
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.commit()
    
    print("✅ Created schema: raw")

def load_to_postgres(df):
    """Load DataFrame to Postgres"""
    
    if df is None or df.empty:
        print("❌ No data to load")
        return
    
    print("\n📤 Loading to Postgres...")
    
    conn = get_postgres_connection()
    
    # Create schema
    create_raw_schema(conn)
    
    # Drop and recreate table
    with conn.cursor() as cur:
        # Drop table
        cur.execute("DROP TABLE IF EXISTS raw.crypto_prices CASCADE")
        conn.commit()
        
        # Create table
        cur.execute("""
            CREATE TABLE raw.crypto_prices (
                id VARCHAR(50),
                symbol VARCHAR(10),
                name VARCHAR(100),
                current_price NUMERIC,
                market_cap NUMERIC,
                total_volume NUMERIC,
                price_change_24h NUMERIC,
                last_updated TIMESTAMP,
                _airbyte_extracted_at TIMESTAMP
            )
        """)
        conn.commit()
    
    print("   ✅ Created table: raw.crypto_prices")
    
    # Insert data row by row (more reliable than COPY)
    with conn.cursor() as cur:
        for idx, row in df.iterrows():
            cur.execute("""
                INSERT INTO raw.crypto_prices (
                    id, symbol, name, current_price, market_cap,
                    total_volume, price_change_24h, last_updated,
                    _airbyte_extracted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.get('id'),
                row.get('symbol'),
                row.get('name'),
                row.get('current_price'),
                row.get('market_cap'),
                row.get('total_volume'),
                row.get('price_change_24h'),
                row.get('last_updated'),
                row.get('_airbyte_extracted_at')
            ))
        
        conn.commit()
    
    print(f"   ✅ Loaded {len(df)} records")
    
    # Verify
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw.crypto_prices")
        count = cur.fetchone()[0]
        print(f"   ✅ Verified {count} records in table")
    
    conn.close()
  
  
def main():
    """Load raw data from MinIO to Postgres"""
    
    print("🔄 RAW DATA LOADER - MinIO → Postgres")
    print("=" * 60)
    
    # Load from MinIO
    df = load_latest_from_minio()
    
    if df is not None:
        # Load to Postgres
        load_to_postgres(df)
        
        print("\n" + "=" * 60)
        print("✅ Raw data loaded successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  cd dbt_fortress")
        print("  dbt run")

if __name__ == "__main__":
    main()
