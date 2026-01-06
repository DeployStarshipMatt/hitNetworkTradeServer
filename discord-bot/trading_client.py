"""
Trading Server Client Module

Handles communication with the Trading Server.
Self-contained - can switch from REST to message queue without affecting other modules.
"""
import requests
import logging
from typing import Optional, Dict, Any
import time

# Add parent directory to path for shared imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.models import TradeSignal, TradeResponse

logger = logging.getLogger(__name__)


class TradingServerClient:
    """
    Client for communicating with the Trading Server.
    
    Handles retries, error handling, and response parsing.
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 10, max_retries: int = 3):
        """
        Initialize Trading Server client.
        
        Args:
            base_url: Base URL of Trading Server (e.g., http://localhost:8000)
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        })
        
        self.stats = {
            'requests_sent': 0,
            'requests_succeeded': 0,
            'requests_failed': 0,
            'retries': 0
        }
    
    def send_signal(self, signal: TradeSignal) -> TradeResponse:
        """
        Send trade signal to Trading Server.
        
        Args:
            signal: TradeSignal object to send
            
        Returns:
            TradeResponse from server
        """
        self.stats['requests_sent'] += 1
        
        endpoint = f"{self.base_url}/api/v1/trade"
        payload = signal.to_dict()
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.stats['retries'] += 1
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                logger.info(f"Sending signal to {endpoint}: {signal.symbol} {signal.side}")
                
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                
                # Check HTTP status
                if response.status_code == 200:
                    self.stats['requests_succeeded'] += 1
                    data = response.json()
                    logger.info(f"Server response: {data.get('message', 'Success')}")
                    return TradeResponse.from_dict(data)
                
                elif response.status_code == 401:
                    # Authentication error - don't retry
                    logger.error("Authentication failed - check API key")
                    self.stats['requests_failed'] += 1
                    return TradeResponse(
                        success=False,
                        signal_id=signal.signal_id,
                        message="Authentication failed",
                        error_code="AUTH_ERROR"
                    )
                
                elif response.status_code == 400:
                    # Bad request - don't retry
                    logger.error(f"Bad request: {response.text}")
                    self.stats['requests_failed'] += 1
                    return TradeResponse(
                        success=False,
                        signal_id=signal.signal_id,
                        message=f"Invalid signal: {response.text}",
                        error_code="VALIDATION_ERROR"
                    )
                
                else:
                    # Server error - retry
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"Server error (attempt {attempt + 1}): {last_error}")
                    continue
                    
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                continue
                
            except requests.exceptions.ConnectionError:
                last_error = "Connection failed"
                logger.warning(f"Connection failed (attempt {attempt + 1})")
                continue
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                continue
        
        # All retries exhausted
        self.stats['requests_failed'] += 1
        logger.error(f"All retry attempts exhausted. Last error: {last_error}")
        return TradeResponse(
            success=False,
            signal_id=signal.signal_id,
            message=f"Failed to send signal: {last_error}",
            error_code="NETWORK_ERROR",
            error_details=last_error
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if Trading Server is reachable.
        
        Returns:
            Health check response or error dict
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset client statistics."""
        self.stats = {
            'requests_sent': 0,
            'requests_succeeded': 0,
            'requests_failed': 0,
            'retries': 0
        }


if __name__ == "__main__":
    # Test the client
    logging.basicConfig(level=logging.INFO)
    
    client = TradingServerClient(
        base_url="http://localhost:8000",
        api_key="test_key"
    )
    
    # Test health check
    print("Testing health check...")
    health = client.health_check()
    print(f"Health: {health}")
    
    # Test sending signal
    print("\nTesting signal send...")
    test_signal = TradeSignal(
        symbol="BTC-USDT",
        side="long",
        entry_price=60000.0,
        stop_loss=58000.0,
        take_profit=65000.0,
        size=0.01
    )
    
    response = client.send_signal(test_signal)
    print(f"Response: {response.to_dict()}")
    print(f"\nStats: {client.get_stats()}")
