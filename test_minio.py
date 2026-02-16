# test_minio.py
"""
Test MinIO S3-compatible API
Uses environment variables for secure credential management
"""

import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_minio_client():
    """
    Create MinIO client using environment variables
    
    Environment variables required:
    - MINIO_ROOT_USER: MinIO access key
    - MINIO_ROOT_PASSWORD: MinIO secret key
    - MINIO_API_PORT: MinIO API port (default: 9000)
    """
    
    # Get credentials from environment
    access_key = os.getenv("MINIO_ROOT_USER")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    api_port = os.getenv("MINIO_API_PORT", "9000")
    
    # Validate credentials exist
    if not access_key or not secret_key:
        raise ValueError(
            "MinIO credentials not found! "
            "Make sure MINIO_ROOT_USER and MINIO_ROOT_PASSWORD "
            "are set in your .env file"
        )
    
    # Initialize MinIO client
    client = Minio(
        f"localhost:{api_port}",
        access_key=access_key,
        secret_key=secret_key,
        secure=False  # No HTTPS in local dev
    )
    
    return client

def test_minio():
    """Test basic MinIO operations"""
    
    print("🔐 Loading credentials from environment variables...")
    
    try:
        client = get_minio_client()
        print("✅ MinIO client initialized securely")
    except ValueError as e:
        print(f"❌ {e}")
        return
    except Exception as e:
        print(f"❌ Error connecting to MinIO: {e}")
        return
    
    bucket_name = "test-bucket"
    
    # 1. Create bucket if doesn't exist
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket already exists: {bucket_name}")
    except S3Error as e:
        print(f"❌ Error creating bucket: {e}")
        return
    
    # 2. Upload a test file
    test_content = "Hello from Sovereign Data Fortress! 🏰\n"
    test_content += "This is S3-compatible object storage running locally.\n"
    test_content += "Credentials loaded securely from environment variables.\n"
    
    try:
        # Write content to a temporary file
        with open("/tmp/test.txt", "w") as f:
            f.write(test_content)
        
        # Upload to MinIO
        client.fput_object(
            bucket_name,
            "test-files/hello.txt",
            "/tmp/test.txt"
        )
        print(f"✅ Uploaded file: test-files/hello.txt")
    except S3Error as e:
        print(f"❌ Error uploading: {e}")
        return
    
    # 3. List objects in bucket
    try:
        objects = client.list_objects(bucket_name, recursive=True)
        print(f"\n📦 Objects in '{bucket_name}':")
        for obj in objects:
            print(f"  - {obj.object_name} ({obj.size} bytes)")
    except S3Error as e:
        print(f"❌ Error listing objects: {e}")
        return
    
    # 4. Download the file
    try:
        client.fget_object(
            bucket_name,
            "test-files/hello.txt",
            "/tmp/downloaded.txt"
        )
        
        # Read and print content
        with open("/tmp/downloaded.txt", "r") as f:
            content = f.read()
        
        print(f"\n📄 Downloaded content:")
        print(content)
        print("✅ Download successful!")
    except S3Error as e:
        print(f"❌ Error downloading: {e}")
        return
    
    print("\n🎉 All MinIO tests passed!")
    print("🔒 Security note: Credentials were never exposed in code")

if __name__ == "__main__":
    test_minio()
