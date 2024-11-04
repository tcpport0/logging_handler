from typing import Dict, Any, Optional
import logging
from datetime import datetime
from .base import BaseLogger

class AppLogger(BaseLogger):
    _instance = None

    @classmethod
    def get(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        # Set up basic logging
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(self.config.LOG_LEVEL)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)
            
        # Add Splunk handler if configured
        if self.config.SPLUNK_URL and self.config.SPLUNK_EVENTS_TOKEN:
            from .splunk_logger import SafeSplunkLogger
            self.splunk_logger = SafeSplunkLogger()
        else:
            self.splunk_logger = None

    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        """Implementation of abstract _log method"""
        context = context or {}
        enriched_context = self.get_base_context()
        enriched_context.update(context)

        # Log to console
        log_func = getattr(self.logger, level)
        log_func(f"{message} | context={enriched_context}", exc_info=exc_info)

        # Log to Splunk if configured
        if self.splunk_logger:
            try:
                if exc_info:
                    import traceback
                    enriched_context['exception'] = {
                        'type': type(exc_info).__name__,
                        'message': str(exc_info),
                        'traceback': traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__)
                    }
                self.splunk_logger.log(message, level=level, **enriched_context)
            except Exception as e:
                self.logger.error(f"Failed to log to Splunk: {str(e)}")

    # Convenience methods
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self._log('debug', message, context, exc_info)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self._log('info', message, context, exc_info)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self._log('warning', message, context, exc_info)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self._log('error', message, context, exc_info)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self._log('critical', message, context, exc_info)