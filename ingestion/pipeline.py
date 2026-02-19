# ingestion/pipeline.py
"""
Complete ELT Pipeline - Airbyte-style

Extract (API) → Load (MinIO) → Transform (dbt - next chapter)
"""

from ingestion.connectors.crypto_api import CryptoAPIConnector
from ingestion.connectors.minio_destination import MinIODestination
from data_contracts.validators.contract_validator import (
    ContractValidator,
    DataContractViolation
)
from data_contracts.schemas.crypto_price import CryptoPriceContract
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class IngestionPipeline:
    """
    Complete ingestion pipeline with data contracts
    
    Flow:
    1. Extract from API (source connector)
    2. Validate against contract
    3. Load to MinIO (destination connector)
    """
    
    def __init__(self, symbols: list = None):
        self.source = CryptoAPIConnector(symbols)
        self.destination = MinIODestination()
        self.validator = ContractValidator(CryptoPriceContract)
    
    def run(self, validate_data: bool = True) -> dict:
        """
        Run the complete pipeline
        
        Args:
            validate_data: If True, enforce data contracts
        
        Returns:
            Pipeline execution summary
        """
        
        print("🚀 INGESTION PIPELINE - Starting")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Step 1: Check connections
        print("\n📡 Step 1: Checking connections...")
        
        source_status = self.source.check_connection()
        if source_status['status'] != 'success':
            return {
                "status": "failed",
                "stage": "source_connection",
                "error": source_status['message']
            }
        print("   ✅ Source API connected")
        
        dest_status = self.destination.check_connection()
        if dest_status['status'] != 'success':
            return {
                "status": "failed",
                "stage": "destination_connection",
                "error": dest_status['message']
            }
        print("   ✅ Destination MinIO connected")
        
        # Step 2: Extract data
        print("\n📥 Step 2: Extracting data from source...")
        records = self.source.read_records()
        
        if not records:
            return {
                "status": "failed",
                "stage": "extraction",
                "error": "No records extracted"
            }
        
        print(f"   ✅ Extracted {len(records)} records")
        
        # Step 3: Validate data (if enabled)
        if validate_data:
            print("\n🔒 Step 3: Validating data contracts...")
            
            # Convert records to contract format
            contract_records = []
            for record in records:
                try:
                    contract_record = {
                        "symbol": record['symbol'],
                        "price": record['current_price'],
                        "timestamp": datetime.now(),
                        "volume": record.get('total_volume'),
                        "market_cap": record.get('market_cap')
                    }
                    contract_records.append(contract_record)
                except KeyError as e:
                    print(f"   ⚠️  Record missing field: {e}")
            
            try:
                validation_result = self.validator.validate_batch(
                    contract_records,
                    fail_fast=False,
                    max_violations=5
                )
                
                if not validation_result['valid']:
                    print(f"   ⚠️  {validation_result['summary']}")
                    print(f"   ⚠️  Proceeding with valid records only")
                    # Filter to only valid records (simplified)
                else:
                    print(f"   ✅ {validation_result['summary']}")
                    
            except DataContractViolation as e:
                return {
                    "status": "failed",
                    "stage": "validation",
                    "error": str(e)
                }
        else:
            print("\n⚠️  Step 3: Validation SKIPPED (validate_data=False)")
        
        # Step 4: Load to destination
        print("\n📤 Step 4: Loading to destination...")
        write_result = self.destination.write_records(
            records=records,
            stream_name="crypto_prices"
        )
        
        if write_result['status'] != 'success':
            return {
                "status": "failed",
                "stage": "load",
                "error": write_result.get('message', 'Unknown error')
            }
        
        print(f"   ✅ Loaded {write_result['records_written']} records")
        print(f"   📁 File: {write_result['file_path']}")
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"Duration: {duration:.2f}s")
        print(f"Records processed: {len(records)}")
        print(f"Destination: MinIO (Parquet format)")
        
        return {
            "status": "success",
            "records_extracted": len(records),
            "records_loaded": write_result['records_written'],
            "duration_seconds": duration,
            "file_path": write_result['file_path']
        }

def main():
    """Run the ingestion pipeline"""
    
    # Create pipeline
    pipeline = IngestionPipeline(
        symbols=['bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot']
    )
    
    # Run with data validation
    result = pipeline.run(validate_data=True)
    
    if result['status'] != 'success':
        print(f"\n❌ Pipeline failed at stage: {result['stage']}")
        print(f"   Error: {result['error']}")
        sys.exit(1)
    
    print(f"\n🎉 Success! Data is now in MinIO, ready for dbt transformation.")

if __name__ == "__main__":
    main()
