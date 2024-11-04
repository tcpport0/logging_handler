# Python Logging Handler

A Python logging handler with built-in support for Splunk events and metrics, with automatic context enrichment and fallback handling.

## Features

- Unified logging interface for both console and Splunk
- Automatic context enrichment with environment information
- Support for both events and metrics
- Built-in fallback logging when Splunk is unavailable
- Configurable retry logic for server errors
- Timezone-aware timestamps
- Exception tracking with full stack traces

## Installation
```
pip install logging-handler
```

## Configuration

Configure via environment variables:

# Required Settings
```
export APP_NAME="your-app-name"
export ENVIRONMENT="production"  # or development, staging, testing
export SPLUNK_HOST="your-splunk-host"
export SPLUNK_EVENTS_TOKEN="your-events-token"
export SPLUNK_METRICS_TOKEN="your-metrics-token"

# Optional Settings
export LOG_LEVEL="INFO"
export SPLUNK_VERIFY_SSL="true"
export SPLUNK_TIMEOUT="2"
export SERVICE_VERSION="1.0.0"

# Optional Context Fields
export POD_NAME="pod-123"
export NODE_NAME="node-1"
export SERVICE_NAME="auth-service"
export AWS_REGION="us-west-2"
```

## Usage

### Basic Logging
```
from logging_handler import logger

# Simple logging
logger.info("User logged in", context={"user_id": "123"})
logger.error("Database connection failed", context={"db": "users"})

# Logging with exception tracking
try:
    result = 1 / 0
except Exception as e:
    logger.error("Division failed", context={"value": 0}, exc_info=e)
```
### Metrics
```
from logging_handler import metrics

# Simple metric
metrics.emit("api.response_time", 0.234)

# Metric with dimensions
metrics.emit(
    "order.total", 
    99.99,
    customer_type="premium",
    region="us-west",
    order_id="ORD-123"
)
```
## Automatic Context

The following context is automatically added to all logs and metrics:
```
{
    'app_name': 'your-app-name',
    'environment': 'production',
    'timestamp': '2024-04-11T15:30:45.123456+00:00',
    'service_version': '1.0.0',  # if SERVICE_VERSION is set
    'pod_name': 'pod-123',       # if POD_NAME is set
    'node_name': 'node-1',       # if NODE_NAME is set
    'service_name': 'auth',      # if SERVICE_NAME is set
    'region': 'us-west-2'        # if AWS_REGION is set
}
```
## Error Handling

The handler includes built-in fallback logging:

# If Splunk is unavailable, logs fall back to console
```
logger.error("API call failed")  # Still logs to console
```
# Metrics also have fallback handling
```
try:
    metrics.emit("api.errors", 1)
except Exception as e:
    # Error is logged to fallback logger
    pass
```
## Development

# Install development dependencies
```
pip install -e ".[dev]"
```
# Run tests
```
pytest
```
# Run with specific environment
```
ENVIRONMENT=development pytest
```
## License

MIT