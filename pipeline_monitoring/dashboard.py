# pipeline_monitoring/dashboard.py
"""
Simple monitoring dashboard for circuit breakers
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline_monitoring.circuit_breaker import CircuitBreaker, CircuitState
from ingestion.pipeline import IngestionPipeline
from datetime import datetime

def display_circuit_status(breaker: CircuitBreaker):
    """Display circuit breaker status"""
    
    status = breaker.get_status()
    
    # State emoji
    state_emoji = {
        "closed": "🟢",
        "open": "🔴",
        "half_open": "🟡"
    }
    
    print(f"\n{'='*60}")
    print(f"Circuit Breaker: {status['name']}")
    print(f"{'='*60}")
    print(f"State: {state_emoji.get(status['state'], '⚪')} {status['state'].upper()}")
    print(f"Failures: {status['failure_count']}/{status['failure_threshold']}")
    
    if status['last_success']:
        print(f"Last Success: {status['last_success']}")
    if status['last_failure']:
        print(f"Last Failure: {status['last_failure']}")
    
    if status['recent_failures']:
        print(f"\nRecent Failures ({len(status['recent_failures'])}):")
        for f in status['recent_failures'][-3:]:
            print(f"  - {f['timestamp']}: {f['error']}")
    
    print(f"{'='*60}\n")

def main():
    """Monitor pipeline circuit breakers"""
    
    print("📊 PIPELINE MONITORING DASHBOARD")
    print("=" * 60)
    
    # Get pipeline and its circuit breaker
    pipeline = IngestionPipeline()
    
    # Display status
    display_circuit_status(pipeline.circuit_breaker)
    
    # Show if pipeline can run
    if pipeline.circuit_breaker.is_open():
        print("⚠️  WARNING: Pipeline is STOPPED by circuit breaker")
        print("   Manual intervention required to fix issues")
        print("   After fixing, reset with: breaker.reset()")
    else:
        print("✅ Pipeline is operational")
        print("   Circuit breaker: CLOSED")

if __name__ == "__main__":
    main()
