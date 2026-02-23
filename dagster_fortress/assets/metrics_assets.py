# dagster_fortress/assets/metrics_assets.py
"""
Metrics and observability assets
"""

from dagster import (
    asset,
    AssetExecutionContext,
    Output,
    MetadataValue,
    AssetObservation
)
from datetime import datetime

@asset(
    name="pipeline_health_metrics",
    description="Overall pipeline health and performance metrics",
    group_name="observability"
)
def pipeline_health_metrics(context: AssetExecutionContext) -> Output[dict]:
    """
    Calculate pipeline health metrics
    
    Tracks:
    - Success rate
    - Average duration
    - Data freshness
    - Error rate
    """
    
    # In production, these would come from real monitoring
    metrics = {
        "success_rate": 99.5,
        "avg_duration_minutes": 2.3,
        "data_freshness_hours": 0.5,
        "error_rate": 0.5,
        "last_updated": datetime.now().isoformat()
    }
    
    context.log.info(f"📊 Pipeline health: {metrics['success_rate']}% success rate")
    
    return Output(
        value=metrics,
        metadata={
            "success_rate": MetadataValue.float(metrics['success_rate']),
            "avg_duration": MetadataValue.text(f"{metrics['avg_duration_minutes']} minutes"),
            "data_freshness": MetadataValue.text(f"{metrics['data_freshness_hours']} hours"),
            "metrics": MetadataValue.json(metrics)
        }
    )

@asset(
    name="data_quality_score",
    description="Aggregate data quality score across all assets",
    group_name="observability"
)
def data_quality_score(context: AssetExecutionContext) -> Output[float]:
    """
    Calculate overall data quality score
    
    Based on:
    - Test pass rate
    - Completeness
    - Freshness
    - Accuracy
    """
    
    # In production, aggregate from actual test results
    quality_components = {
        "test_pass_rate": 100.0,  # All tests passing
        "completeness": 98.5,      # 98.5% of expected data
        "freshness": 99.0,         # 99% within SLA
        "accuracy": 99.9           # 99.9% accurate
    }
    
    # Weighted average
    overall_score = (
        quality_components["test_pass_rate"] * 0.4 +
        quality_components["completeness"] * 0.3 +
        quality_components["freshness"] * 0.2 +
        quality_components["accuracy"] * 0.1
    )
    
    context.log.info(f"✅ Data quality score: {overall_score:.1f}/100")
    
    return Output(
        value=overall_score,
        metadata={
            "overall_score": MetadataValue.float(overall_score),
            "test_pass_rate": MetadataValue.float(quality_components["test_pass_rate"]),
            "completeness": MetadataValue.float(quality_components["completeness"]),
            "freshness": MetadataValue.float(quality_components["freshness"]),
            "quality_breakdown": MetadataValue.json(quality_components)
        }
    )
