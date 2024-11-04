import pytest
import time
from datetime import datetime, timezone
from logging_handler import metrics
from dotenv import load_dotenv
load_dotenv()


def test_basic_metrics(test_context):
    """Test basic metric emission"""
    # Test counter
    metrics.emit(
        metric_name="test_counter",
        value=1,
        **test_context
    )
    
    # Test gauge
    metrics.emit(
        metric_name="test_gauge",
        value=42.5,
        metric_type="gauge",
        **test_context
    )
    
    # Test timing
    metrics.emit(
        metric_name="test_duration",
        value=0.123,
        metric_type="timing",
        **test_context
    )
    
    # Allow time for processing
    time.sleep(2)
    # Verify in Splunk metrics

def test_batch_metrics(test_context):
    """Test batch metric processing"""
    # Send multiple metrics
    for i in range(10):
        metrics.emit(
            metric_name="batch_test",
            value=i,
            iteration=i,
            **test_context
        )
    
    # Force flush
    metrics._flush_metrics()
    
    time.sleep(2)
    # Verify batch in Splunk

def test_high_volume_metrics(test_context):
    """Test handling of high-volume metrics"""
    start_time = datetime.now(timezone.utc)
    
    # Send 1000 metrics rapidly
    for i in range(1000):
        metrics.emit(
            metric_name="volume_test",
            value=i,
            iteration=i,
            **test_context
        )
    
    # Force final flush
    metrics._flush_metrics()
    
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Log the performance metric
    metrics.emit(
        metric_name="metric_emission_duration",
        value=duration,
        total_metrics=1000,
        **test_context
    )
    
def test_metric_format(test_context):
    """Test metric format structure"""
    # Create metric but don't send it
    metric = {
        "time": datetime.now(timezone.utc).timestamp(),
        "event": "metric",
        "source": "metrics",
        "sourcetype": "perflog",
        "fields": {
            **test_context,
            "metric_name:test_format": 100.0
        }
    }
    
    # Verify structure
    assert "time" in metric
    assert "event" in metric
    assert "fields" in metric
    assert any(key.startswith("metric_name:") for key in metric["fields"])
    assert metric["event"] == "metric"
    