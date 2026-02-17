# test_localstack.py
"""
Test LocalStack AWS Simulation
Demonstrates that code written for LocalStack
works identically on real AWS (just change endpoint)
"""

import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

# LocalStack configuration
LOCALSTACK_ENDPOINT = os.getenv(
    "LOCALSTACK_ENDPOINT",
    "http://localhost:4566"
)

# AWS Credentials (fake for LocalStack)
AWS_CONFIG = {
    "endpoint_url": LOCALSTACK_ENDPOINT,
    "region_name": "us-east-1",
    "aws_access_key_id": "test",
    "aws_secret_access_key": "test"
}

def get_s3_client():
    """Create S3 client pointing to LocalStack"""
    return boto3.client('s3', **AWS_CONFIG)

def get_sqs_client():
    """Create SQS client pointing to LocalStack"""
    return boto3.client('sqs', **AWS_CONFIG)

def get_lambda_client():
    """Create Lambda client pointing to LocalStack"""
    return boto3.client('lambda', **AWS_CONFIG)

def test_s3():
    """Test S3 operations on LocalStack"""
    print("\n🪣 Testing S3 (AWS Simple Storage Service)")
    print("─" * 50)

    s3 = get_s3_client()
    bucket_name = "sovereign-data-fortress-raw"

    # 1. Create bucket
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created S3 bucket: {bucket_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket already exists: {bucket_name}")
        else:
            print(f"❌ Error: {e}")
            return False

    # 2. Upload raw data file
    raw_data = {
        "source": "crypto_api",
        "timestamp": "2024-01-15T10:00:00Z",
        "data": [
            {"symbol": "BTC", "price": 42000.00, "volume": 1234567},
            {"symbol": "ETH", "price": 2500.00, "volume": 987654},
            {"symbol": "SOL", "price": 100.00, "volume": 456789}
        ]
    }

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key="raw/crypto/2024/01/15/prices.json",
            Body=json.dumps(raw_data, indent=2),
            ContentType="application/json"
        )
        print(f"✅ Uploaded raw data to S3")
    except ClientError as e:
        print(f"❌ Upload error: {e}")
        return False

    # 3. List objects
    try:
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix="raw/"
        )
        objects = response.get('Contents', [])
        print(f"\n📦 Objects in S3 bucket '{bucket_name}':")
        for obj in objects:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")
    except ClientError as e:
        print(f"❌ List error: {e}")
        return False

    # 4. Download and read data
    try:
        response = s3.get_object(
            Bucket=bucket_name,
            Key="raw/crypto/2024/01/15/prices.json"
        )
        content = json.loads(response['Body'].read())
        print(f"\n📄 Downloaded data from S3:")
        for item in content['data']:
            print(f"  {item['symbol']}: ${item['price']:,.2f}")
    except ClientError as e:
        print(f"❌ Download error: {e}")
        return False

    print(f"\n✅ S3 tests passed!")
    return True

def test_sqs():
    """Test SQS (Simple Queue Service) on LocalStack"""
    print("\n📬 Testing SQS (AWS Simple Queue Service)")
    print("─" * 50)

    sqs = get_sqs_client()
    queue_name = "data-pipeline-events"

    # 1. Create queue
    try:
        response = sqs.create_queue(
            QueueName=queue_name,
            Attributes={
                'MessageRetentionPeriod': '86400',
                'VisibilityTimeout': '30'
            }
        )
        queue_url = response['QueueUrl']
        print(f"✅ Created SQS queue: {queue_name}")
    except ClientError as e:
        print(f"❌ Error: {e}")
        return False

    # 2. Send messages (pipeline events)
    events = [
        {"event": "ingestion_started", "source": "crypto_api"},
        {"event": "validation_passed", "records": 3},
        {"event": "transformation_complete", "tables": ["stg_prices", "fct_daily"]}
    ]

    for event in events:
        try:
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(event),
                MessageAttributes={
                    'source': {
                        'DataType': 'String',
                        'StringValue': 'data-fortress'
                    }
                }
            )
        except ClientError as e:
            print(f"❌ Send error: {e}")

    print(f"✅ Sent {len(events)} pipeline events to SQS")

    # 3. Receive messages
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=1
        )
        messages = response.get('Messages', [])
        print(f"\n📨 Received {len(messages)} messages:")
        for msg in messages:
            body = json.loads(msg['Body'])
            print(f"  - Event: {body['event']}")

            # Delete message after processing
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
    except ClientError as e:
        print(f"❌ Receive error: {e}")
        return False

    print(f"\n✅ SQS tests passed!")
    return True

def test_cost_comparison():
    """
    Show theoretical AWS cost vs LocalStack cost
    This is the KEY insight for recruiters
    """
    print("\n💰 Cost Comparison: LocalStack vs AWS")
    print("─" * 50)

    operations = {
        "S3 PUT requests": {
            "count": 10000,
            "aws_cost_per_1000": 0.005,
            "localstack_cost": 0.0
        },
        "S3 GET requests": {
            "count": 50000,
            "aws_cost_per_1000": 0.0004,
            "localstack_cost": 0.0
        },
        "S3 Storage (1 GB/month)": {
            "count": 1,
            "aws_cost_per_1000": 23.0,
            "localstack_cost": 0.0
        },
        "SQS Messages": {
            "count": 100000,
            "aws_cost_per_1000": 0.0004,
            "localstack_cost": 0.0
        },
        "Lambda Invocations": {
            "count": 50000,
            "aws_cost_per_1000": 0.0002,
            "localstack_cost": 0.0
        }
    }

    total_aws_cost = 0
    print(f"\n{'Service':<30} {'Count':>10} {'AWS Cost':>12} {'LocalStack':>12}")
    print("-" * 65)

    for service, details in operations.items():
        aws_cost = (details['count'] / 1000) * details['aws_cost_per_1000']
        total_aws_cost += aws_cost
        print(
            f"{service:<30} "
            f"{details['count']:>10,} "
            f"${aws_cost:>10.4f} "
            f"${details['localstack_cost']:>10.2f}"
        )

    print("-" * 65)
    print(f"\n{'TOTAL (per month)':<30} {'':>10} ${total_aws_cost:>10.4f} ${'0.00':>10}")
    print(f"\n💡 Monthly savings: ${total_aws_cost:.4f}")
    print(f"💡 Annual savings: ${total_aws_cost * 12:.4f}")
    print(f"\n✅ LocalStack = Same learning, $0 cost!")

def show_portability():
    """Show how code is identical between LocalStack and AWS"""
    print("\n🔄 Code Portability Demo")
    print("─" * 50)
    print("""
    # Development (LocalStack) → Production (AWS)
    # Only ONE line changes:

    # DEV (LocalStack)
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',  # ← This line
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    # PROD (AWS)
    s3 = boto3.client(
        's3',
        # endpoint_url removed = defaults to AWS
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    # Rest of code is IDENTICAL ✅
    s3.create_bucket(Bucket='my-bucket')
    s3.put_object(Bucket='my-bucket', Key='data.json', Body=data)
    """)

    print("✅ This is cloud-agnostic development!")

def main():
    """Run all LocalStack tests"""
    print("🏰 SOVEREIGN DATA FORTRESS - LocalStack Tests")
    print("=" * 60)
    print(f"🌐 AWS Endpoint: {LOCALSTACK_ENDPOINT} (LocalStack simulation)")
    print("💡 These exact same API calls work on real AWS!")
    print("=" * 60)

    # Check LocalStack health
    import urllib.request
    try:
        response = urllib.request.urlopen(
            f"{LOCALSTACK_ENDPOINT}/_localstack/health",
            timeout=5
        )
        health = json.loads(response.read())
        print(f"\n✅ LocalStack is running!")
        print(f"   Services: {', '.join(health.get('services', {}).keys())}")
    except Exception as e:
        print(f"\n❌ LocalStack not reachable: {e}")
        print("   Make sure to run: make infra-up")
        return

    # Run tests
    results = {}
    results['s3'] = test_s3()
    results['sqs'] = test_sqs()

    # Show insights
    test_cost_comparison()
    show_portability()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    all_passed = all(results.values())
    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {service.upper()}: {status}")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("💡 Your code is AWS-ready (zero AWS costs during dev)")
        print("🔄 Deploy to real AWS: Just change endpoint_url")
    print("=" * 60)

if __name__ == "__main__":
    main()
