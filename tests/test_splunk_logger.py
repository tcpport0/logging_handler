import pytest
from datetime import datetime, timezone
import time
from logging_handler import logger
from logging_handler.config import Config
import traceback
from dotenv import load_dotenv
load_dotenv()

def test_basic_logging(test_context):
    """Test basic logging functionality"""
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"Test log message at {timestamp}"
    
    # Test different log levels
    logger.debug(message, context=test_context)
    logger.info(message, context=test_context)
    logger.warning(message, context=test_context)
    logger.error(message, context=test_context)
    
    # Give Splunk time to process
    time.sleep(2)
    
    # Note: Manual verification in Splunk UI needed
    # Search query: source="test_app" test_id="test-123"

def test_exception_logging(test_context):
    """Test exception logging"""
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.error(
            "Test exception occurred",
            context=test_context,
            exc_info=e
        )
    
    time.sleep(2)
    # Verify in Splunk: exception.type="ValueError"

def test_context_enrichment(test_context):
    """Test that optional environment variables are included"""
    config = Config()
    
    # Set some optional environment variables for testing
    import os
    os.environ['SERVICE_VERSION'] = '1.0.0'
    os.environ['REGION'] = 'us-west-2'
    
    message = "Testing context enrichment"
    logger.info(message, context=test_context)
    
    time.sleep(2)
    # Verify in Splunk that service_version and region are present

def test_splunk_connection():
    """Test basic Splunk connectivity"""
    from logging_handler import logger
    from logging_handler.config import Config
    
    config = Config()
    
    # Validate Splunk configuration
    assert config.SPLUNK_URL, "SPLUNK_HOST not configured"
    assert config.SPLUNK_EVENTS_TOKEN, "SPLUNK_EVENTS_TOKEN not configured"
    
    test_message = f"Test connection to Splunk at {datetime.now(timezone.utc).isoformat()}"
    
    try:
        logger.info(test_message, context={
            "test_id": "connection_test",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        print(f"Splunk Connection Error: {str(e)}")
        print(f"Traceback: {''.join(traceback.format_exc())}")
        raise

    # No sleep needed - if it doesn't work, it will fail immediately

def test_direct_splunk_send():
    """Test direct Splunk sending without any wrapper logic"""
    from logging_handler.splunk_base import SplunkBase
    from datetime import datetime
    
    # Create basic splunk sender
    splunk = SplunkBase(endpoint="event")
    
    # Create a simple payload similar to the working curl command
    test_payload = {
        "event": {
            "message": "Direct test event",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "sourcetype": "_json"
    }
    
    # Send directly using _send_to_splunk
    splunk._send_to_splunk(test_payload)
    print("✓ Successfully sent test event to Splunk")
