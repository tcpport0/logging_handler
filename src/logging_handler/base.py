import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from .config import Config

class BaseLogger(ABC):
    """Base class for all logging implementations"""
    
    def __init__(self):
        self.config = Config()  # Use config instance instead of direct env vars
        self.app_name = self.config.APP_NAME or "unknown_app"
        self.environment = self.config.ENVIRONMENT or "development"
        
    def get_base_context(self) -> Dict[str, Any]:
        """Get common context fields from environment"""
        context = {
            'app_name': self.app_name,
            'environment': self.environment,
            'timestamp': datetime.now(timezone.utc).isoformat()  # Add timestamp by default
        }
        
        # Optional fields - only add if they exist
        optional_fields = {
            'service_version': 'SERVICE_VERSION',
            'pod_name': 'POD_NAME',
            'node_name': 'NODE_NAME',
            'container_id': 'CONTAINER_ID',
            'service_name': 'SERVICE_NAME',
            'service_tier': 'SERVICE_TIER',
            'region': 'AWS_REGION',
            'availability_zone': 'AVAILABILITY_ZONE',
            'deployment_id': 'DEPLOYMENT_ID',
            'commit_hash': 'COMMIT_HASH'
        }
        
        # Only add fields that are set in environment
        for field, env_var in optional_fields.items():
            if value := os.getenv(env_var):
                context[field] = value
                
        return context

    @abstractmethod
    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        """Abstract method that all loggers must implement"""
        pass

class AppLogger(BaseLogger):
    _instance = None

    @classmethod
    def get(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        # ... rest of logger initialization ...

    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None):
        """Internal logging method"""
        enriched_context = self.enrich_context(context)
        
        # Log to console
        log_func = getattr(self.logger, level)
        log_func(f"{message} | context={enriched_context}", exc_info=exc_info)
        
        # Log to Splunk if configured
        if self.splunk_logger:
            try:
                if exc_info:
                    enriched_context['exception'] = self.format_exception(exc_info)
                self.splunk_logger.log(message, level=level, **enriched_context)
            except Exception as e:
                self.logger.error(f"Failed to log to Splunk: {str(e)}")

class MetricEmitter(BaseLogger):
    def __init__(self):
        super().__init__()
        from .splunk_logger import SafeSplunkLogger
        self.splunk_logger = SafeSplunkLogger()

    def emit(self, metric_name: str, value: float, **dimensions: Dict[str, Any]):
        try:
            enriched_context = self.enrich_context(dimensions)
            
            payload = {
                "time": datetime.now(timezone.utc).timestamp(),
                "event": "metric",
                "fields": {
                    "metric_name": metric_name,
                    "_value": value,
                    **enriched_context
                }
            }
            
            self.splunk_logger.log(payload)
        except Exception as e:
            from . import logger
            logger.error(f"Failed to emit metric: {metric_name}", 
                        context={"error": str(e)},
                        exc_info=e)
