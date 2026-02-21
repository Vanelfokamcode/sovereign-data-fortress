# pipeline_monitoring/circuit_breaker.py
"""
Circuit Breaker Pattern for Data Pipelines

Prevents bad data from propagating through the system.
Implements fail-fast with automatic alerting.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Pipeline stopped
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """
    Circuit Breaker for data pipelines
    
    Usage:
        breaker = CircuitBreaker(
            name="crypto_ingestion",
            failure_threshold=3,
            recovery_timeout=300
        )
        
        if breaker.is_open():
            raise CircuitBreakerError("Pipeline is stopped")
        
        try:
            result = run_pipeline()
            breaker.record_success()
        except Exception as e:
            breaker.record_failure(e)
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,  # seconds
        alert_callback: Callable = None
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.alert_callback = alert_callback
        
        # State
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # History
        self.failure_history: List[Dict] = []
        self.success_history: List[Dict] = []
    
    def is_open(self) -> bool:
        """Check if circuit is open (pipeline stopped)"""
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).seconds
                if elapsed > self.recovery_timeout:
                    # Move to half-open for testing
                    self.state = CircuitState.HALF_OPEN
                    logger.info(
                        f"🟡 Circuit breaker {self.name} entering HALF-OPEN state"
                    )
                    return False
            return True
        
        return False
    
    def record_success(self):
        """Record successful pipeline run"""
        
        self.last_success_time = datetime.now()
        self.success_history.append({
            "timestamp": self.last_success_time.isoformat(),
            "state": self.state.value
        })
        
        if self.state == CircuitState.HALF_OPEN:
            # Success in half-open → back to closed
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"🟢 Circuit breaker {self.name} CLOSED (recovered)")
        
        logger.info(f"✅ Pipeline {self.name} successful")
    
    def record_failure(self, error: Exception):
        """Record pipeline failure"""
        
        self.last_failure_time = datetime.now()
        self.failure_count += 1
        
        failure_record = {
            "timestamp": self.last_failure_time.isoformat(),
            "error": str(error),
            "error_type": type(error).__name__,
            "failure_count": self.failure_count
        }
        self.failure_history.append(failure_record)
        
        logger.error(
            f"❌ Pipeline {self.name} failed: {error} "
            f"(failure {self.failure_count}/{self.failure_threshold})"
        )
        
        # Check if threshold reached
        if self.failure_count >= self.failure_threshold:
            self._trip_circuit(error)
        
        # Always alert on failure
        if self.alert_callback:
            self.alert_callback(self.name, error, self.state)
    
    def _trip_circuit(self, error: Exception):
        """Trip the circuit breaker (open it)"""
        
        self.state = CircuitState.OPEN
        
        logger.critical(
            f"🔴 CIRCUIT BREAKER OPEN: {self.name} "
            f"(threshold {self.failure_threshold} reached)"
        )
        
        # Alert that circuit is open
        if self.alert_callback:
            self.alert_callback(
                self.name,
                error,
                self.state,
                is_critical=True
            )
    
    def reset(self):
        """Manually reset the circuit breaker"""
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        logger.info(f"🔄 Circuit breaker {self.name} manually RESET")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": self.last_failure_time.isoformat() 
                           if self.last_failure_time else None,
            "last_success": self.last_success_time.isoformat() 
                           if self.last_success_time else None,
            "recent_failures": self.failure_history[-5:],
            "is_open": self.is_open()
        }

# Alert callbacks

def console_alert(name: str, error: Exception, state: CircuitState, is_critical: bool = False):
    """Simple console alert"""
    
    if is_critical:
        print(f"\n{'='*60}")
        print(f"🚨 CRITICAL ALERT: Circuit Breaker OPEN")
        print(f"{'='*60}")
        print(f"Pipeline: {name}")
        print(f"State: {state.value}")
        print(f"Error: {error}")
        print(f"{'='*60}\n")
    else:
        print(f"⚠️  Alert: {name} failed - {error}")

def slack_alert(name: str, error: Exception, state: CircuitState, is_critical: bool = False):
    """Slack webhook alert (simplified)"""
    
    # In production, you'd send to actual Slack webhook
    message = {
        "text": f"🚨 Circuit Breaker: {name}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Pipeline:* {name}\n*State:* {state.value}\n*Error:* {error}"
                }
            }
        ]
    }
    
    logger.info(f"📤 Would send Slack alert: {json.dumps(message, indent=2)}")

# Demo

def demo_circuit_breaker():
    """Demonstrate circuit breaker in action"""
    
    print("🔌 CIRCUIT BREAKER DEMO")
    print("=" * 60)
    
    # Create breaker
    breaker = CircuitBreaker(
        name="demo_pipeline",
        failure_threshold=3,
        recovery_timeout=5,  # 5 seconds for demo
        alert_callback=console_alert
    )
    
    print(f"\nInitial state: {breaker.get_status()['state']}")
    
    # Simulate failures
    print("\n1️⃣  Simulating failures...")
    for i in range(1, 5):
        print(f"\n   Attempt {i}:")
        
        if breaker.is_open():
            print("   ❌ Circuit is OPEN - pipeline stopped")
            break
        
        try:
            # Simulate failure
            raise ValueError(f"Simulated error #{i}")
        except Exception as e:
            breaker.record_failure(e)
    
    # Check status
    print(f"\n2️⃣  Circuit status:")
    status = breaker.get_status()
    print(f"   State: {status['state']}")
    print(f"   Failures: {status['failure_count']}/{status['failure_threshold']}")
    print(f"   Is open: {status['is_open']}")
    
    # Wait for recovery timeout
    if breaker.is_open():
        print(f"\n3️⃣  Waiting {breaker.recovery_timeout}s for recovery timeout...")
        import time
        time.sleep(breaker.recovery_timeout + 1)
        
        print(f"   Circuit state after timeout: {breaker.state.value}")
    
    # Simulate success
    print("\n4️⃣  Simulating successful run...")
    if not breaker.is_open():
        breaker.record_success()
        print(f"   Circuit state: {breaker.state.value}")
    
    print("\n" + "=" * 60)
    print("✅ Circuit breaker demo complete")

if __name__ == "__main__":
    demo_circuit_breaker()
