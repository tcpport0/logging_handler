import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Dict, Any, Optional
from .config import Config
import os
class SplunkBase:
    def __init__(self, endpoint: str = "event"):
        self.config = Config()
        self.endpoint = endpoint
        self.port = os.getenv("SPLUNK_PORT", None)
        if self.port:
            self.hec_url = f"https://{self.config.SPLUNK_URL}:{self.port}/services/collector"
        else:
            self.hec_url = f"https://{self.config.SPLUNK_URL}/services/collector"
        
        # Use appropriate token based on endpoint
        self.token = (self.config.SPLUNK_METRICS_TOKEN 
                     if endpoint == "metric" 
                     else self.config.SPLUNK_EVENTS_TOKEN)
                     
        self.headers = {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json"
        }
        
        # Setup session with retry logic
        self.session = self._setup_session()
        
        # Validate connection
        self._validate_connection()

    def _setup_session(self) -> requests.Session:
        """Configure session with minimal retry logic"""
        session = requests.Session()
        
        # Simplified retry strategy - only retry once for server errors
        retry_strategy = Retry(
            total=0,  # No retries for most cases
            status_forcelist=[500, 502, 503, 504]  # Only retry for server errors
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session

    def _send_to_splunk(self, payload: Dict[str, Any]) -> None:
        """Send data to Splunk with detailed error handling"""
        print(payload)
        try:
            response = self.session.post(
                self.hec_url,
                headers=self.headers,
                json=payload,
                verify=self.config.SPLUNK_VERIFY_SSL,
                timeout=self.config.SPLUNK_TIMEOUT
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = f"""
            Splunk logging failed:
            Error: {str(e)}
            URL: {self.hec_url}
            Response: {getattr(e.response, 'text', 'No response')}
            Status Code: {getattr(e.response, 'status_code', 'No status code')}
            Payload: {payload}
            """
            raise RuntimeError(error_msg) from e

    def _validate_connection(self):
        """Validate Splunk connection on initialization"""
        try:
            test_payload = {
                "event": {
                    "message": "Connection test",
                    "_validation": True
                }
            }
            self._send_to_splunk(test_payload)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Splunk at {self.hec_url}: {str(e)}") from e