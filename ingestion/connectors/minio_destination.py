# ingestion/connectors/minio_destination.py
"""
MinIO Destination Connector - Airbyte-style

Writes data to MinIO (S3-compatible) in Parquet format
"""

import os
import json
import pandas as pd
from minio import Minio
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class MinIODestination:
    """
    Destination connector for MinIO
    
    Writes records to MinIO in Parquet format
    (columnar, compressed, analytics-optimized)
    """
    
    def __init__(self):
        self.endpoint = f"localhost:{os.getenv('MINIO_API_PORT', '9000')}"
        self.access_key = os.getenv('MINIO_ROOT_USER', 'minioadmin')
        self.secret_key = os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin123')
        
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )
        
        self.bucket = "raw-data"
    
    def check_connection(self) -> Dict[str, Any]:
        """Test MinIO connection"""
        try:
            # Try to list buckets
            buckets = list(self.client.list_buckets())
            return {
                "status": "success",
                "message": f"Connected. {len(buckets)} buckets available."
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection error: {str(e)}"
            }
    
    def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            print(f"✅ Created bucket: {self.bucket}")
        else:
            print(f"✅ Bucket exists: {self.bucket}")
    
    def write_records(
        self,
        records: List[Dict[str, Any]],
        stream_name: str
    ) -> Dict[str, Any]:
        """
        Write records to MinIO as Parquet
        
        Args:
            records: List of dictionaries
            stream_name: Name of the data stream
        
        Returns:
            Write status
        """
        
        if not records:
            return {
                "status": "success",
                "records_written": 0,
                "message": "No records to write"
            }
        
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stream_name}/{timestamp}.parquet"
            local_path = f"/tmp/{stream_name}_{timestamp}.parquet"
            
            # Write to Parquet locally first
            df.to_parquet(local_path, index=False, compression='snappy')
            
            # Upload to MinIO
            self.client.fput_object(
                self.bucket,
                filename,
                local_path
            )
            
            # Cleanup local file
            os.remove(local_path)
            
            print(f"✅ Wrote {len(records)} records to s3://{self.bucket}/{filename}")
            
            return {
                "status": "success",
                "records_written": len(records),
                "file_path": f"s3://{self.bucket}/{filename}",
                "file_size_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Write error: {str(e)}",
                "records_written": 0
            }

def demo_destination():
    """Demo the MinIO destination"""
    
    print("📦 MINIO DESTINATION CONNECTOR DEMO")
    print("=" * 60)
    
    destination = MinIODestination()
    
    # Check connection
    print("\n1️⃣  Checking connection...")
    status = destination.check_connection()
    print(f"   Status: {status['status']}")
    print(f"   Message: {status['message']}")
    
    if status['status'] != 'success':
        print("❌ Cannot connect to MinIO. Make sure it's running:")
        print("   Run: make infra-up")
        return
    
    # Sample records
    sample_records = [
        {
            "symbol": "BTC",
            "price": 42000.50,
            "volume": 1234567,
            "timestamp": datetime.now().isoformat()
        },
        {
            "symbol": "ETH",
            "price": 2500.00,
            "volume": 987654,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Write records
    print("\n2️⃣  Writing records...")
    result = destination.write_records(
        records=sample_records,
        stream_name="crypto_prices"
    )
    
    print(f"   Status: {result['status']}")
    print(f"   Records written: {result['records_written']}")
    if result['status'] == 'success':
        print(f"   File path: {result['file_path']}")
        print(f"   File size: {result['file_size_mb']:.2f} MB")
    
    print("\n" + "=" * 60)
    print("✅ Destination demo complete!")

if __name__ == "__main__":
    demo_destination()
