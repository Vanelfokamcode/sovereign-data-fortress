# data_contracts/validators/contract_validator.py
"""
Data Contract Validator

This module validates incoming data against defined contracts.
If validation fails, the pipeline STOPS (fail fast).
"""

from typing import List, Dict, Any, Tuple
from pydantic import ValidationError
import pandas as pd
from datetime import datetime
import json

class DataContractViolation(Exception):
    """Raised when data violates contract"""
    pass

class ContractValidator:
    """
    Validates data against Pydantic schemas
    
    Usage:
        validator = ContractValidator(CryptoPriceContract)
        validator.validate_batch(data_list)
    """
    
    def __init__(self, contract_schema):
        self.contract_schema = contract_schema
        self.violations = []
    
    def validate_single(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single record
        
        Returns:
            (is_valid, error_message)
        """
        try:
            self.contract_schema(**data)
            return True, ""
        except ValidationError as e:
            error_msg = self._format_validation_error(e, data)
            return False, error_msg
    
    def validate_batch(
        self,
        data_list: List[Dict[str, Any]],
        fail_fast: bool = True,
        max_violations: int = 10
    ) -> Dict[str, Any]:
        """
        Validate a batch of records
        
        Args:
            data_list: List of records to validate
            fail_fast: If True, stop on first violation
            max_violations: Maximum violations to tolerate
        
        Returns:
            {
                'valid': bool,
                'total_records': int,
                'valid_records': int,
                'invalid_records': int,
                'violations': List[str],
                'summary': str
            }
        """
        total = len(data_list)
        valid_count = 0
        violations = []
        
        for idx, record in enumerate(data_list):
            is_valid, error_msg = self.validate_single(record)
            
            if is_valid:
                valid_count += 1
            else:
                violation = {
                    'record_index': idx,
                    'record': record,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }
                violations.append(violation)
                
                # Fail fast mode
                if fail_fast:
                    raise DataContractViolation(
                        f"Data contract violation at record {idx}:\n"
                        f"{error_msg}\n"
                        f"Record: {record}\n\n"
                        f"Pipeline STOPPED to prevent bad data propagation."
                    )
                
                # Too many violations
                if len(violations) >= max_violations:
                    raise DataContractViolation(
                        f"Too many violations ({len(violations)}).\n"
                        f"Pipeline STOPPED.\n"
                        f"First violation: {violations[0]['error']}"
                    )
        
        invalid_count = total - valid_count
        
        result = {
            'valid': invalid_count == 0,
            'total_records': total,
            'valid_records': valid_count,
            'invalid_records': invalid_count,
            'violations': violations,
            'violation_rate': invalid_count / total if total > 0 else 0,
            'summary': self._generate_summary(total, valid_count, invalid_count)
        }
        
        return result
    
    def validate_dataframe(
        self,
        df: pd.DataFrame,
        fail_fast: bool = True
    ) -> Dict[str, Any]:
        """Validate a pandas DataFrame"""
        records = df.to_dict('records')
        return self.validate_batch(records, fail_fast=fail_fast)
    
    def _format_validation_error(
        self,
        error: ValidationError,
        data: Dict[str, Any]
    ) -> str:
        """Format Pydantic validation error for readability"""
        errors = error.errors()
        formatted = []
        
        for err in errors:
            field = '.'.join(str(x) for x in err['loc'])
            msg = err['msg']
            formatted.append(f"  - {field}: {msg}")
        
        return "\n".join(formatted)
    
    def _generate_summary(
        self,
        total: int,
        valid: int,
        invalid: int
    ) -> str:
        """Generate human-readable summary"""
        if invalid == 0:
            return f"✅ All {total} records passed validation"
        else:
            rate = (invalid / total) * 100
            return (
                f"⚠️  {invalid}/{total} records failed validation ({rate:.1f}%)\n"
                f"Valid: {valid}, Invalid: {invalid}"
            )

def demo_contract_validation():
    """Demonstrate data contract validation"""
    from data_contracts.schemas.crypto_price import (
        CryptoPriceContract,
        INVALID_EXAMPLES
    )
    
    print("🔒 DATA CONTRACT VALIDATION DEMO")
    print("=" * 60)
    
    validator = ContractValidator(CryptoPriceContract)
    
    # Test valid data
    print("\n✅ Testing VALID data:")
    valid_data = {
        "symbol": "BTC",
        "price": 42000.50,
        "timestamp": datetime.now(),
        "volume": 1234567.89
    }
    is_valid, error = validator.validate_single(valid_data)
    print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"   Error: {error}")
    
    # Test invalid data
    print("\n❌ Testing INVALID data examples:")
    for example in INVALID_EXAMPLES:
        print(f"\n  Case: {example['reason']}")
        is_valid, error = validator.validate_single(example['data'])
        if not is_valid:
            print(f"   ✅ Correctly REJECTED")
            print(f"   Reason: {error}")
        else:
            print(f"   ❌ ERROR: Should have been rejected!")
    
    # Test batch validation
    print("\n\n📦 Testing BATCH validation:")
    
    batch_data = [
        {"symbol": "BTC", "price": 42000, "timestamp": datetime.now()},
        {"symbol": "ETH", "price": 2500, "timestamp": datetime.now()},
        {"symbol": "btc", "price": 100, "timestamp": datetime.now()},  # Invalid: lowercase
        {"symbol": "SOL", "price": 100, "timestamp": datetime.now()},
    ]
    
    try:
        result = validator.validate_batch(
            batch_data,
            fail_fast=False,
            max_violations=10
        )
        print(f"\n{result['summary']}")
        if not result['valid']:
            print(f"\nViolations found:")
            for v in result['violations']:
                print(f"  Record {v['record_index']}: {v['error']}")
    except DataContractViolation as e:
        print(f"\n❌ Pipeline stopped: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Key Takeaway:")
    print("   Data contracts PREVENT bad data from entering your warehouse")
    print("   Better to fail fast than to have wrong data in production!")

if __name__ == "__main__":
    demo_contract_validation()
