# analytics/duckdb_demo.py
"""
DuckDB Analytics Demo
Shows the power of columnar analytics vs traditional databases
"""

import duckdb
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

def create_sample_data():
    """Create sample crypto price data for analytics"""

    print("📊 Generating sample crypto data...")

    # Generate 1 million rows of crypto data
    import random
    from datetime import datetime, timedelta

    rows = []
    symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
    start_date = datetime(2023, 1, 1)

    for i in range(100000):  # 100k rows
        symbol = random.choice(symbols)
        date = start_date + timedelta(hours=i)
        base_price = {
            'BTC': 30000, 'ETH': 2000,
            'SOL': 50, 'ADA': 0.5, 'DOT': 8
        }[symbol]

        price = base_price * (1 + random.uniform(-0.05, 0.05))
        volume = random.uniform(1000, 100000)

        rows.append({
            'timestamp': date.isoformat(),
            'symbol': symbol,
            'price': round(price, 2),
            'volume': round(volume, 2),
            'market_cap': round(price * volume * 1000, 2)
        })

    df = pd.DataFrame(rows)

    # Save as Parquet (columnar format)
    os.makedirs('data/analytics', exist_ok=True)
    df.to_parquet('data/analytics/crypto_prices.parquet', index=False)
    df.to_csv('data/analytics/crypto_prices.csv', index=False)

    print(f"✅ Generated {len(df):,} rows")
    print(f"✅ Saved as Parquet: data/analytics/crypto_prices.parquet")
    print(f"✅ Saved as CSV: data/analytics/crypto_prices.csv")

    return df

def demo_duckdb_speed():
    """Compare DuckDB vs Pandas performance"""

    print("\n⚡ Performance Comparison: DuckDB vs Pandas")
    print("─" * 60)

    # DuckDB reading Parquet
    print("\n🦆 DuckDB reading Parquet:")
    start = time.time()

    conn = duckdb.connect()
    result = conn.execute("""
        SELECT
            symbol,
            COUNT(*) as data_points,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(MIN(price), 2) as min_price,
            ROUND(MAX(price), 2) as max_price,
            ROUND(SUM(volume), 2) as total_volume
        FROM read_parquet('data/analytics/crypto_prices.parquet')
        GROUP BY symbol
        ORDER BY avg_price DESC
    """).df()

    duckdb_time = time.time() - start
    print(result.to_string(index=False))
    print(f"\n⏱️  DuckDB time: {duckdb_time:.4f} seconds")

    # Pandas reading CSV
    print("\n🐼 Pandas reading CSV:")
    start = time.time()

    df = pd.read_csv('data/analytics/crypto_prices.csv')
    result_pandas = df.groupby('symbol').agg(
        data_points=('price', 'count'),
        avg_price=('price', 'mean'),
        min_price=('price', 'min'),
        max_price=('price', 'max'),
        total_volume=('volume', 'sum')
    ).round(2).sort_values('avg_price', ascending=False)

    pandas_time = time.time() - start
    print(result_pandas.to_string())
    print(f"\n⏱️  Pandas time: {pandas_time:.4f} seconds")

    # Comparison
    if pandas_time > 0:
        speedup = pandas_time / duckdb_time
        print(f"\n🏆 DuckDB is {speedup:.1f}x faster than Pandas!")

def demo_duckdb_analytics():
    """Show real analytics use cases with DuckDB"""

    print("\n📈 Real Analytics Use Cases")
    print("─" * 60)

    conn = duckdb.connect()

    # 1. Time series analysis
    print("\n1️⃣  Daily Price Trends (BTC)")
    result = conn.execute("""
        SELECT
            strftime(timestamp::TIMESTAMP, '%Y-%m') as month,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(MAX(price), 2) as max_price,
            ROUND(MIN(price), 2) as min_price,
            ROUND(
                (MAX(price) - MIN(price)) / MIN(price) * 100,
                2
            ) as volatility_pct
        FROM read_parquet('data/analytics/crypto_prices.parquet')
        WHERE symbol = 'BTC'
        GROUP BY month
        ORDER BY month
        LIMIT 6
    """).df()
    print(result.to_string(index=False))

    # 2. Market dominance
    print("\n2️⃣  Market Cap Dominance")
    result = conn.execute("""
        WITH total_market AS (
            SELECT SUM(market_cap) as total
            FROM read_parquet('data/analytics/crypto_prices.parquet')
        )
        SELECT
            symbol,
            ROUND(SUM(market_cap) / 1e9, 2) as market_cap_billions,
            ROUND(
                SUM(market_cap) / (SELECT total FROM total_market) * 100,
                2
            ) as dominance_pct
        FROM read_parquet('data/analytics/crypto_prices.parquet')
        GROUP BY symbol
        ORDER BY market_cap_billions DESC
    """).df()
    print(result.to_string(index=False))

    # 3. Anomaly detection
    print("\n3️⃣  Price Anomalies (> 3% change)")
    result = conn.execute("""
        WITH price_changes AS (
            SELECT
                symbol,
                timestamp,
                price,
                LAG(price) OVER (
                    PARTITION BY symbol
                    ORDER BY timestamp
                ) as prev_price
            FROM read_parquet('data/analytics/crypto_prices.parquet')
        )
        SELECT
            symbol,
            COUNT(*) as anomaly_count,
            ROUND(AVG(
                ABS(price - prev_price) / prev_price * 100
            ), 2) as avg_change_pct
        FROM price_changes
        WHERE prev_price IS NOT NULL
          AND ABS(price - prev_price) / prev_price > 0.03
        GROUP BY symbol
        ORDER BY anomaly_count DESC
    """).df()
    print(result.to_string(index=False))

    # 4. Rolling averages (moving average)
    print("\n4️⃣  7-Period Moving Average (ETH)")
    result = conn.execute("""
        SELECT
            timestamp,
            price,
            ROUND(AVG(price) OVER (
                PARTITION BY symbol
                ORDER BY timestamp
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 2) as moving_avg_7,
            ROUND(price - AVG(price) OVER (
                PARTITION BY symbol
                ORDER BY timestamp
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 2) as deviation_from_ma
        FROM read_parquet('data/analytics/crypto_prices.parquet')
        WHERE symbol = 'ETH'
        ORDER BY timestamp
        LIMIT 10
    """).df()
    print(result.to_string(index=False))

def demo_duckdb_with_minio():
    """Show DuckDB reading directly from MinIO (S3)"""

    print("\n🗄️  DuckDB + MinIO Integration")
    print("─" * 60)

    minio_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
    minio_password = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
    minio_port = os.getenv("MINIO_API_PORT", "9000")

    try:
        conn = duckdb.connect()

        # Configure MinIO as S3-compatible endpoint
        conn.execute(f"""
            INSTALL httpfs;
            LOAD httpfs;

            SET s3_endpoint='localhost:{minio_port}';
            SET s3_access_key_id='{minio_user}';
            SET s3_secret_access_key='{minio_password}';
            SET s3_use_ssl=false;
            SET s3_url_style='path';
        """)

        # First upload a parquet file to MinIO
        from minio import Minio
        minio_client = Minio(
            f"localhost:{minio_port}",
            access_key=minio_user,
            secret_key=minio_password,
            secure=False
        )

        # Create bucket if not exists
        if not minio_client.bucket_exists("analytics"):
            minio_client.make_bucket("analytics")

        # Upload parquet file
        minio_client.fput_object(
            "analytics",
            "crypto/prices.parquet",
            "data/analytics/crypto_prices.parquet"
        )
        print("✅ Uploaded Parquet to MinIO")

        # Now query DIRECTLY from MinIO with DuckDB!
        result = conn.execute("""
            SELECT
                symbol,
                COUNT(*) as records,
                ROUND(AVG(price), 2) as avg_price
            FROM read_parquet('s3://analytics/crypto/prices.parquet')
            GROUP BY symbol
            ORDER BY avg_price DESC
        """).df()

        print("✅ DuckDB queried Parquet DIRECTLY from MinIO!")
        print("\n📊 Results from MinIO:")
        print(result.to_string(index=False))
        print("\n💡 No loading needed - DuckDB reads from S3 directly!")

    except Exception as e:
        print(f"⚠️  MinIO integration test skipped: {e}")
        print("   (Make sure MinIO is running: make infra-up)")

def demo_file_formats():
    """Compare file formats for analytics"""

    print("\n📁 File Format Comparison")
    print("─" * 60)

    conn = duckdb.connect()
    os.makedirs('data/analytics', exist_ok=True)

    # Check if files exist
    if not os.path.exists('data/analytics/crypto_prices.parquet'):
        print("⚠️ Run create_sample_data() first")
        return

    # Get file sizes
    parquet_size = os.path.getsize(
        'data/analytics/crypto_prices.parquet'
    ) / 1024 / 1024
    csv_size = os.path.getsize(
        'data/analytics/crypto_prices.csv'
    ) / 1024 / 1024

    print(f"\n📊 File sizes for 100,000 rows:")
    print(f"  CSV (row format):     {csv_size:.2f} MB")
    print(f"  Parquet (columnar):   {parquet_size:.2f} MB")

    compression_ratio = csv_size / parquet_size
    print(f"\n  Parquet is {compression_ratio:.1f}x smaller than CSV!")

    # Query speed comparison
    print(f"\n⚡ Query speed:")

    start = time.time()
    conn.execute(
        "SELECT AVG(price) FROM read_csv_auto"
        "('data/analytics/crypto_prices.csv')"
    ).fetchone()
    csv_time = time.time() - start

    start = time.time()
    conn.execute(
        "SELECT AVG(price) FROM read_parquet"
        "('data/analytics/crypto_prices.parquet')"
    ).fetchone()
    parquet_time = time.time() - start

    print(f"  CSV query time:     {csv_time:.4f}s")
    print(f"  Parquet query time: {parquet_time:.4f}s")

    if parquet_time > 0:
        speedup = csv_time / parquet_time
        print(f"\n  Parquet is {speedup:.1f}x faster than CSV!")

    print("""
    Why Parquet for Data Engineering?
    ✅ Columnar = faster analytics queries
    ✅ Compressed = less storage cost
    ✅ Schema = type safety
    ✅ Standard = works with Spark, BigQuery, DuckDB
    """)

def main():
    """Run all DuckDB demos"""

    print("🏰 SOVEREIGN DATA FORTRESS - DuckDB Analytics")
    print("=" * 60)
    print("🦆 DuckDB: The SQLite of Analytics")
    print("=" * 60)

    # 1. Generate sample data
    create_sample_data()

    # 2. Speed comparison
    demo_duckdb_speed()

    # 3. Analytics use cases
    demo_duckdb_analytics()

    # 4. File format comparison
    demo_file_formats()

    # 5. MinIO integration
    demo_duckdb_with_minio()

    print("\n" + "=" * 60)
    print("🎉 DuckDB Demo Complete!")
    print("=" * 60)
    print("""
    Key Takeaways:
    ✅ DuckDB = columnar analytics (vs PostgreSQL row storage)
    ✅ 10-100x faster than Pandas for analytics
    ✅ Reads directly from Parquet/CSV/JSON/S3
    ✅ No server needed (embedded in Python)
    ✅ Perfect for Data Engineering pipelines
    ✅ Integrates with MinIO (S3-compatible)
    """)

if __name__ == "__main__":
    main()
