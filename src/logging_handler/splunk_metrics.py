from typing import Dict, Any, Union, List, Optional
from datetime import datetime, timezone
from collections import defaultdict
from .base import BaseLogger

class MetricEmitter(BaseLogger):
    def __init__(self):
        super().__init__()
        from .splunk_logger import SafeSplunkLogger
        self.splunk_logger = SafeSplunkLogger(endpoint="metric")
        self._batch: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        """Implementation of abstract method"""
        # Metrics use emit() instead of _log()
        pass
        
    def emit(self, metric_name: str, value: Union[int, float], **dimensions: Any) -> None:
        enriched_context = self.get_base_context()
        enriched_context.update(dimensions)
        
        metric = {
            "time": datetime.now(timezone.utc).timestamp(),
            "event": "metric",
            "source": "metrics",
            "sourcetype": "perflog",
            "fields": {
                **enriched_context,
                f"metric_name:{metric_name}": float(value)
            }
        }
        
        self.splunk_logger.log(metric)
    
    def _flush_metrics(self, metric_name: Optional[str] = None) -> None:
        """Flush metrics to Splunk"""
        try:
            if metric_name:
                metrics = self._batch.pop(metric_name, [])
                if metrics:
                    for metric in metrics:
                        self.splunk_logger.log(metric)
            else:
                for name, metrics in self._batch.items():
                    if metrics:
                        for metric in metrics:
                            self.splunk_logger.log(metric)
                self._batch.clear()
                
        except Exception as e:
            from . import logger  # Import here to avoid circular import
            logger.error(f"Failed to flush metrics", exc_info=e)

