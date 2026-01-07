"""
BloFin Trading Client Module

Handles all BloFin API interactions for order execution.
Self-contained - implements complete trading logic independently.
"""
import requests
import json
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
import time

from blofin_auth import BloFinAuth

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order side mapping."""
    BUY = "buy"
    SELL = "sell"


class TradeMode(Enum):
    """Position mode."""
    CROSS = "cross"
    ISOLATED = "isolated"


class BloFinClient:
    """
    BloFin API client for trading operations.
    
    Handles order placement, position management, and account queries.
    """
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str, 
                 base_url: str = "https://openapi.blofin.com", timeout: int = 10):
        """
        Initialize BloFin client.
        
        Args:
            api_key: BloFin API key
            secret_key: BloFin secret key
            passphrase: BloFin passphrase
            base_url: API base URL (use demo URL for testing)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth = BloFinAuth(api_key, secret_key, passphrase)
        
        self.session = requests.Session()
        
        self.stats = {
            'orders_placed': 0,
            'orders_failed': 0,
            'api_calls': 0,
            'api_errors': 0
        }
    
    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated API request.
        
        Args:
            method: HTTP method
            path: API path
            body: Request body
            
        Returns:
            Response data
            
        Raises:
            Exception: On API error
        """
        self.stats['api_calls'] += 1
        
        url = f"{self.base_url}{path}"
        try:
            if method.upper() == "GET":
                headers = self.auth.get_headers(method, path, None, body, debug=False)
                response = self.session.get(url, headers=headers, params=body, timeout=self.timeout) if body else self.session.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                    headers = self.auth.get_headers(method, path.rstrip('/'), body=body, debug=True)
                    # Serialize body to JSON string to match signature
                    import uuid
                    doc_order = ["instId", "marginMode", "positionSide", "side", "orderType", "price", "size"]
                    sorted_body = {k: body[k] for k in doc_order if k in body}
                    for k in body:
                        if k not in sorted_body:
                            sorted_body[k] = body[k]
                    body_str = json.dumps(sorted_body, separators=(',', ':'))
                    
                    allowed_headers = [
                        'ACCESS-KEY', 'ACCESS-SIGN', 'ACCESS-TIMESTAMP', 'ACCESS-NONCE', 'ACCESS-PASSPHRASE', 'Content-Type'
                    ]
                    filtered_headers = {k: v for k, v in headers.items() if k in allowed_headers}
                    print("\n=== BloFin POST Trade Debug ===")
                    print(f"POST URL: {url}")
                    print(f"Payload: {body_str}")
                    print("Headers:")
                    for k, v in filtered_headers.items():
                        print(f"  {k}: {v}")
                    print("==============================\n")
                    # Use data= with pre-serialized JSON to preserve key order for signature
                    response = self.session.post(url, headers=filtered_headers, data=body_str, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            # Parse response
            data = response.json()
            # Check BloFin API response code
            if data.get('code') == '0':
                logger.debug(f"API call successful: {method} {path}")
                return data.get('data', {})
            else:
                self.stats['api_errors'] += 1
                error_msg = data.get('msg', 'Unknown error')
                error_code = data.get('code', 'UNKNOWN')
                logger.error(f"BloFin API error {error_code}: {error_msg}")
                raise Exception(f"BloFin API error {error_code}: {error_msg}")
        except requests.exceptions.Timeout:
            self.stats['api_errors'] += 1
            logger.error(f"Request timeout: {method} {path}")
            raise Exception("Request timeout")
        except requests.exceptions.RequestException as e:
            self.stats['api_errors'] += 1
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def place_market_order(self, symbol: str, side: str, size: float, 
                          trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            side: Order side (buy/sell)
            size: Order size in contracts
            trade_mode: cross or isolated
            
        Returns:
            Order response with order_id
        """
        # Normalize side
        if side.lower() in ["long", "buy"]:
            api_side = "buy"
        elif side.lower() in ["short", "sell"]:
            api_side = "sell"
        else:
            raise ValueError(f"Invalid side: {side}")
        
        payload = {
            "instId": symbol,
            "marginMode": trade_mode,
            "positionSide": "net",  # Required: net for One-way Mode, long/short for Hedge Mode
            "side": api_side,
            "orderType": "market",
            "size": str(size)
        }
        
        logger.info(f"Placing market order: {api_side} {size} {symbol}")
        
        try:
            response = self._request("POST", "/api/v1/trade/order", payload)
            self.stats['orders_placed'] += 1
            
            # Response is a list of orders, get the first one
            if isinstance(response, list) and len(response) > 0:
                order_data = response[0]
            else:
                order_data = response
            
            order_id = order_data.get('ordId') if isinstance(order_data, dict) else None
            logger.info(f"✅ Order placed successfully: {order_id}")
            
            return {
                'order_id': order_id,
                'symbol': symbol,
                'side': api_side,
                'size': size,
                'type': 'market',
                'status': 'submitted'
            }
        
        except Exception as e:
            self.stats['orders_failed'] += 1
            logger.error(f"❌ Failed to place order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, size: float, price: float,
                         trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair
            side: Order side
            size: Order size
            price: Limit price
            trade_mode: cross or isolated
            
        Returns:
            Order response
        """
        # Normalize side
        if side.lower() in ["long", "buy"]:
            api_side = "buy"
        elif side.lower() in ["short", "sell"]:
            api_side = "sell"
        else:
            raise ValueError(f"Invalid side: {side}")
        
        payload = {
            "instId": symbol,
            "positionSide": "net",  # Required: net for One-way Mode, long/short for Hedge Mode
            "tdMode": trade_mode,
            "side": api_side,
            "ordType": "limit",
            "sz": str(size),
            "px": str(price)
        }
        
        logger.info(f"Placing limit order: {api_side} {size} {symbol} @ {price}")
        
        try:
            response = self._request("POST", "/api/v1/trade/order", payload)
            self.stats['orders_placed'] += 1
            
            # Response is a list of orders, get the first one
            if isinstance(response, list) and len(response) > 0:
                order_data = response[0]
            else:
                order_data = response
            
            order_id = order_data.get('ordId') if isinstance(order_data, dict) else None
            logger.info(f"✅ Limit order placed: {order_id}")
            
            return {
                'order_id': order_id,
                'symbol': symbol,
                'side': api_side,
                'size': size,
                'price': price,
                'type': 'limit',
                'status': 'submitted'
            }
        
        except Exception as e:
            self.stats['orders_failed'] += 1
            logger.error(f"❌ Failed to place limit order: {e}")
            raise
    
    def set_stop_loss(self, symbol: str, side: str, size: float, trigger_price: float,
                     trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Set stop loss order.
        
        Args:
            symbol: Trading pair
            side: Order side (opposite of position)
            size: Order size
            trigger_price: Stop loss trigger price
            trade_mode: cross or isolated
            
        Returns:
            Order response
        """
        payload = {
            "instId": symbol,
            "tdMode": trade_mode,
            "side": side,
            "ordType": "stop_market",
            "sz": str(size),
            "triggerPx": str(trigger_price)
        }
        
        logger.info(f"Setting stop loss: {symbol} @ {trigger_price}")
        
        try:
            response = self._request("POST", "/api/v1/trade/order", payload)
            order_id = response.get('ordId')
            logger.info(f"✅ Stop loss set: {order_id}")
            return {'order_id': order_id, 'type': 'stop_loss'}
        
        except Exception as e:
            logger.error(f"❌ Failed to set stop loss: {e}")
            raise
    
    def set_take_profit(self, symbol: str, side: str, size: float, trigger_price: float,
                       trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Set take profit order.
        
        Args:
            symbol: Trading pair
            side: Order side (opposite of position)
            size: Order size
            trigger_price: Take profit trigger price
            trade_mode: cross or isolated
            
        Returns:
            Order response
        """
        payload = {
            "instId": symbol,
            "tdMode": trade_mode,
            "side": side,
            "ordType": "stop_market",
            "sz": str(size),
            "triggerPx": str(trigger_price)
        }
        
        logger.info(f"Setting take profit: {symbol} @ {trigger_price}")
        
        try:
            response = self._request("POST", "/api/v1/trade/order", payload)
            order_id = response.get('ordId')
            logger.info(f"✅ Take profit set: {order_id}")
            return {'order_id': order_id, 'type': 'take_profit'}
        
        except Exception as e:
            logger.error(f"❌ Failed to set take profit: {e}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Account balance information
        """
        try:
            response = self._request("GET", "/api/v1/account/balance")
            return response
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get open positions.
        
        Returns:
            List of open positions
        """
        try:
            response = self._request("GET", "/api/v1/account/positions")
            return response if isinstance(response, list) else []
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order status information
        """
        try:
            response = self._request("GET", f"/api/v1/trade/order?instId={symbol}&ordId={order_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return self.stats.copy()


if __name__ == "__main__":
    # Test client (requires valid credentials)
    logging.basicConfig(level=logging.INFO)
    
    # This will fail without real credentials - just for structure testing
    client = BloFinClient(
        api_key="test",
        secret_key="test",
        passphrase="test",
        base_url="https://demo-trading-openapi.blofin.com"
    )
    
    print(f"BloFin client initialized")
    print(f"Base URL: {client.base_url}")
    print(f"Auth valid: {client.auth.validate_credentials()}")
