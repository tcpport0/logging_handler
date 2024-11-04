# src/logging_handler/config.py
from typing import Optional
import os

class Config:
    def __init__(self):
        # Core settings
        self.APP_NAME = os.getenv("APP_NAME", "unknown_app")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Splunk settings
        self.SPLUNK_URL = os.getenv("SPLUNK_HOST", "splunk-hec.tisrv.com")
        self.SPLUNK_EVENTS_TOKEN = os.getenv("SPLUNK_EVENTS_TOKEN")
        self.SPLUNK_METRICS_TOKEN = os.getenv("SPLUNK_METRICS_TOKEN")
        self.SPLUNK_TIMEOUT = int(os.getenv("SPLUNK_TIMEOUT", "2"))
        self.SPLUNK_VERIFY_SSL = os.getenv("SPLUNK_VERIFY_SSL", "true").lower() == "true"
        self.SPLUNK_BATCH_SIZE = int(os.getenv("SPLUNK_BATCH_SIZE", "10"))
        
        # Performance settings
        self.ENABLE_ASYNC = os.getenv("ENABLE_ASYNC", "false").lower() == "true"
        self.MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "10000"))
        
        self.validate()
    
    def validate(self):
        """Validate required configuration"""
        if self.ENVIRONMENT not in ["development", "staging", "production", "testing"]:
            raise ValueError(f"Invalid environment: {self.ENVIRONMENT}")
            
        if not self._is_valid_log_level(self.LOG_LEVEL):
            raise ValueError(f"Invalid log level: {self.LOG_LEVEL}")
            
        self._validate_splunk_config()
    
    def _is_valid_log_level(self, level: str) -> bool:
        """Validate log level"""
        return level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def _validate_splunk_config(self):
        """Validate Splunk-specific configuration"""
        if not self.SPLUNK_URL:
            raise ValueError("SPLUNK_HOST is required")
            
        if not self.SPLUNK_EVENTS_TOKEN:
            raise ValueError("SPLUNK_EVENTS_TOKEN is required")
            
        if not self.SPLUNK_METRICS_TOKEN:
            raise ValueError("SPLUNK_METRICS_TOKEN is required")

    @classmethod
    def as_dict(cls):
        """Return configuration as a dictionary for easy access."""
        return {k: getattr(cls, k) for k in dir(cls) if not k.startswith("__") and not callable(getattr(cls, k))}
