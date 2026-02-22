# dagster_fortress/resources/minio_resource.py
"""
MinIO resource for Dagster

Provides connection to MinIO for asset materialization
"""

import os
from minio import Minio
from dagster import ConfigurableResource
from pydantic import Field

class MinIOResource(ConfigurableResource):
    """
    MinIO S3-compatible storage resource
    
    Usage:
        @asset
        def my_asset(minio: MinIOResource):
            client = minio.get_client()
            # Use client...
    """
    
    endpoint: str = Field(
        default="localhost:9000",
        description="MinIO endpoint"
    )
    
    access_key: str = Field(
        default="minioadmin",
        description="MinIO access key"
    )
    
    secret_key: str = Field(
        default="minioadmin123",
        description="MinIO secret key"
    )
    
    secure: bool = Field(
        default=False,
        description="Use HTTPS"
    )
    
    def get_client(self) -> Minio:
        """Get MinIO client"""
        return Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
    
    def ensure_bucket(self, bucket_name: str):
        """Ensure bucket exists"""
        client = self.get_client()
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            return f"Created bucket: {bucket_name}"
        return f"Bucket exists: {bucket_name}"
