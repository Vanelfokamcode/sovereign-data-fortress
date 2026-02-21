# Pipeline Monitoring & Circuit Breakers

## Overview

Circuit breakers protect the data pipeline from cascading failures
by stopping execution when errors are detected.

## How It Works

### 3 States

1. **CLOSED** 🟢 (Normal)
   - Pipeline runs normally
   - All validations passing
   - Ready to process data

2. **OPEN** 🔴 (Stopped)
   - Pipeline automatically stopped
   - Too many failures detected
   - Alerts sent to team
   - Requires manual intervention

3. **HALF-OPEN** 🟡 (Testing)
   - After recovery timeout
   - Pipeline attempts to run
   - If successful → CLOSED
   - If fails → OPEN

### Configuration
```python
CircuitBreaker(
    name="my_pipeline",
    failure_threshold=3,     # Stop after 3 failures
    recovery_timeout=300,    # Wait 5 min before retry
    alert_callback=slack_alert  # Alert function
)
```

### Usage in Pipeline
```python
# Check before running
if circuit_breaker.is_open():
    raise CircuitBreakerError("Pipeline stopped")

try:
    result = run_pipeline()
    circuit_breaker.record_success()
except Exception as e:
    circuit_breaker.record_failure(e)
```

## Benefits

✅ **Fail Fast**: Stop immediately on error  
✅ **Prevent Cascade**: Don't corrupt downstream data  
✅ **Auto Alert**: Team notified instantly  
✅ **Self-Healing**: Auto-retry after timeout  
✅ **Audit Trail**: Full failure history  

## Commands
```bash
# Monitor status
make monitor-circuits

# Test functionality
make test-circuit-breaker

# Check in code
python pipeline_monitoring/dashboard.py
```

## Real-World Example

**Without Circuit Breaker:**
```
Day 1: API returns bad data
Day 2-14: Pipeline loads bad data daily
Day 15: Business notices dashboard wrong
Cost: 2 weeks of wrong decisions
```

**With Circuit Breaker:**
```
Minute 1: API returns bad data
Minute 2: Circuit breaker opens, alerts sent
Minute 30: Team fixes issue, resets breaker
Cost: 30 minutes, zero bad data
```

## Integration Points

- Ingestion pipeline: Before loading to MinIO
- dbt pipeline: After transformation tests
- Alerting: Slack, email, PagerDuty
- Monitoring: Grafana dashboards
