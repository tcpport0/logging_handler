import logging
import traceback
from datetime import datetime, timezone
from .splunk_base import SplunkBase
from typing import Dict, Any, Optional
import sys

class SplunkHandler(logging.Handler):
    def __init__(self, verify_ssl=True):
        super().__init__()
        self.splunk_logger = SafeSplunkLogger(verify_ssl=verify_ssl)
        
    def emit(self, record):
        try:
            # Get the formatted message
            message = self.format(record)
            
            # Extract additional fields
            extra_fields = {
                'logger_name': record.name,
                'function': record.funcName,
                'file': record.filename,
                'line_number': record.lineno,
                'thread': record.threadName,
            }
            
            # Add extra attributes from record if they exist
            if hasattr(record, 'extra_fields'):
                extra_fields.update(record.extra_fields)

            # Handle exceptions
            if record.exc_info:
                extra_fields['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }

            self.splunk_logger.log(
                message=message,
                level=record.levelname.lower(),
                **extra_fields
            )
        except Exception as e:
            # Fallback to sys.stderr
            fallback_logger = logging.getLogger('splunk_handler_fallback')
            fallback_logger.error(f"Failed to send logs to Splunk: {str(e)}")


class SafeSplunkLogger(SplunkBase):
    """
    A wrapper around SplunkLogger that never raises exceptions
    """
    def __init__(self, endpoint: str = "event"):
        try:
            super().__init__(endpoint=endpoint)
        except Exception as e:
            self._log_fallback(f"Failed to initialize Splunk logger: {str(e)}")
            
    def log(self, message: Any, level: str = "info", **additional_fields: Any) -> None:
        try:
            if self.endpoint == "metric":
                # For metrics, assume message is already properly formatted
                payload = message
            else:
                # For events, wrap in event structure
                event_data = {
                    "time": datetime.now(timezone.utc).timestamp(),
                    "level": level,
                    "message": message,
                    **additional_fields
                }
                
                payload = {
                    "event": event_data,
                    "sourcetype": "_json"
                }
            
            self._send_to_splunk(payload)
        except Exception as e:
            error_msg = f"""
            Splunk logging failed:
            Message: {message}
            Error: {str(e)}
            Traceback: {''.join(traceback.format_exc())}
            """
            # Log to console for visibility
            print(error_msg, file=sys.stderr)
            # Also log to fallback logger
            self._log_fallback(error_msg)

    def _log_fallback(self, error_message: str) -> None:
        """Fallback logging to stderr when Splunk logging fails"""
        fallback_logger = logging.getLogger('splunk_fallback')
        if not fallback_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            fallback_logger.addHandler(handler)
        fallback_logger.error(error_message)
