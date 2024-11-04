"""Logging handler package with support for Splunk and other services."""

from .base import BaseLogger
from .splunk_metrics import MetricEmitter
from .log_handler import AppLogger

# Export instances
logger = AppLogger.get()
metrics = MetricEmitter()

# Clean up namespace
__all__ = ['logger', 'metrics']
