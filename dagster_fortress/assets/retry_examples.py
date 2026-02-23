# dagster_fortress/assets/retry_examples.py
"""
Examples of different retry strategies for various failure scenarios
"""

from dagster import (
    asset,
    AssetExecutionContext,
    RetryPolicy,
    Backoff,
    Output
)
import time
import random

@asset(
    name="fast_retry_asset",
    description="Fast retries for transient errors (network blips)",
    retry_policy=RetryPolicy(
        max_retries=5,
        delay=10,  # 10 seconds
        backoff=Backoff.LINEAR
    )
)
def fast_retry_asset(context: AssetExecutionContext) -> Output[str]:
    """
    Retry quickly for fast-recovering errors
    
    Use case: Network blips, temporary DNS issues
    Pattern: 10s, 20s, 30s, 40s, 50s
    """
    
    # Simulate transient failure (50% chance)
    if random.random() < 0.5:
        context.log.warning("⚠️  Simulated transient failure - will retry")
        raise Exception("Transient error (network blip)")
    
    context.log.info("✅ Success!")
    return Output(value="Data processed")

@asset(
    name="patient_retry_asset",
    description="Patient retries for slow-recovering errors (API rate limits)",
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=300,  # 5 minutes
        backoff=Backoff.EXPONENTIAL
    )
)
def patient_retry_asset(context: AssetExecutionContext) -> Output[str]:
    """
    Retry slowly for rate-limited APIs
    
    Use case: Rate limited APIs, quota exceeded
    Pattern: 5min, 10min, 20min
    """
    
    context.log.info("Processing with rate limit handling...")
    
    # Simulate rate limit recovery
    if random.random() < 0.3:
        context.log.warning("⚠️  Rate limited - waiting before retry")
        raise Exception("Rate limit exceeded")
    
    return Output(value="Data processed")

@asset(
    name="no_retry_asset",
    description="No retries for permanent errors (bad config, auth failure)",
    retry_policy=RetryPolicy(max_retries=0)
)
def no_retry_asset(context: AssetExecutionContext) -> Output[str]:
    """
    Don't retry for errors that won't resolve
    
    Use case: Authentication failures, bad configuration, invalid data
    """
    
    context.log.info("Processing without retries...")
    
    # Simulate permanent error
    if random.random() < 0.2:
        context.log.error("❌ Permanent error - no retry")
        raise Exception("Invalid API key - fix required")
    
    return Output(value="Data processed")
