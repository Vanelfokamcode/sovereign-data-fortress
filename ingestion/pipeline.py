# ingestion/pipeline.py
"""
Complete ELT Pipeline with Circuit Breaker Protection

Extract (API) → Load (MinIO) → Transform (dbt)
Protected by circuit breaker for automatic failure handling
"""

from ingestion.connectors.crypto_api import CryptoAPIConnector
from ingestion.connectors.minio_destination import MinIODestination
from data_contracts.validators.contract_validator import (
    ContractValidator,
    DataContractViolation
)
from data_contracts.schemas.crypto_price import CryptoPriceContract
from pipeline_monitoring.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    console_alert
)
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class IngestionPipeline:
    """
    Complete ingestion pipeline with data contracts and circuit breaker
    
    Flow:
    1. Check circuit breaker status
    2. Extract from API (source connector)
    3. Validate against contract
    4. Load to MinIO (destination connector)
    5. Record success/failure in circuit breaker
    """
    
    def __init__(self, symbols: list = None):
        self.source = CryptoAPIConnector(symbols)
        self.destination = MinIODestination()
        self.validator = ContractValidator(CryptoPriceContract)
        
        # Circuit breaker for auto-healing
        self.circuit_breaker = CircuitBreaker(
            name="crypto_ingestion",
            failure_threshold=3,
            recovery_timeout=300,  # 5 minutes
            alert_callback=console_alert
        )
    
    def run(self, validate_data: bool = True) -> dict:
        """
        Run the complete pipeline with circuit breaker protection
        
        Args:
            validate_data: If True, enforce data contracts
        
        Returns:
            Pipeline execution summary
        """
        
        print("🚀 INGESTION PIPELINE - Starting")
        print("=" * 60)
        
        # STEP 0: Check circuit breaker FIRST
        if self.circuit_breaker.is_open():
            error_msg = (
                f"🔴 Pipeline stopped by circuit breaker\n"
                f"State: {self.circuit_breaker.state.value}\n"
                f"Failures: {self.circuit_breaker.failure_count}\n"
                f"Last failure: {self.circuit_breaker.last_failure_time}\n"
                f"\nManual intervention required.\n"
                f"After fixing issues, reset with: breaker.reset()"
            )
            print(error_msg)
            raise CircuitBreakerError(error_msg)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Check connections
            print("\n📡 Step 1: Checking connections...")
            
            source_status = self.source.check_connection()
            if source_status['status'] != 'success':
                raise Exception(f"Source connection failed: {source_status['message']}")
            print("   ✅ Source API connected")
            
            dest_status = self.destination.check_connection()
            if dest_status['status'] != 'success':
                raise Exception(f"Destination connection failed: {dest_status['message']}")
            print("   ✅ Destination MinIO connected")
            
            # Step 2: Extract data
            print("\n📥 Step 2: Extracting data from source...")
            records = self.source.read_records()
            
            if not records:
                raise Exception("No records extracted from source")
            
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
                    else:
                        print(f"   ✅ {validation_result['summary']}")
                        
                except DataContractViolation as e:
                    raise Exception(f"Data contract violation: {e}")
            else:
                print("\n⚠️  Step 3: Validation SKIPPED (validate_data=False)")
            
            # Step 4: Load to destination
            print("\n📤 Step 4: Loading to destination...")
            write_result = self.destination.write_records(
                records=records,
                stream_name="crypto_prices"
            )
            
            if write_result['status'] != 'success':
                raise Exception(f"Load failed: {write_result.get('message', 'Unknown error')}")
            
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
            
            # Record success in circuit breaker
            self.circuit_breaker.record_success()
            
            return {
                "status": "success",
                "records_extracted": len(records),
                "records_loaded": write_result['records_written'],
                "duration_seconds": duration,
                "file_path": write_result['file_path'],
                "circuit_breaker_state": self.circuit_breaker.state.value
            }
        
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure(e)
            
            print(f"\n❌ Pipeline failed: {e}")
            print(f"Circuit breaker state: {self.circuit_breaker.state.value}")
            
            return {
                "status": "failed",
                "error": str(e),
                "circuit_breaker_state": self.circuit_breaker.state.value,
                "failure_count": self.circuit_breaker.failure_count
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
        print(f"\n❌ Pipeline failed")
        print(f"   Error: {result.get('error', 'Unknown')}")
        print(f"   Circuit breaker: {result.get('circuit_breaker_state', 'unknown')}")
        sys.exit(1)
    
    print(f"\n🎉 Success! Data is now in MinIO, ready for dbt transformation.")

if __name__ == "__main__":
    main()
