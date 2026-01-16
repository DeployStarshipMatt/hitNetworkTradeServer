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
        
        # Cache for instrument specifications
        self._instrument_cache = {}
        
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
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float, 
                                risk_percent: float = 1.0, leverage: int = 10) -> Dict[str, Any]:
        """
        Calculate position size for specified account risk, ignoring signal leverage.
        Uses TOTAL EQUITY for risk calculation to ensure positions don't oversize.
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Percent of EQUITY to risk (default 1.0)
            leverage: Leverage to use (default 10x for more available margin)
            
        Returns:
            Dict with size, margin_needed, and calculated info
        """
        # Get account balance
        balance_data = self.get_account_balance()
        if not balance_data or 'details' not in balance_data:
            raise Exception("Could not fetch account balance")
        
        # Use TOTAL EQUITY, not available balance
        equity = float(balance_data['details'][0].get('equity', 0))
        available = float(balance_data['details'][0].get('available', 0))
        
        # Calculate risk amount (1% of EQUITY, not available)
        risk_amount = equity * (risk_percent / 100)
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            raise ValueError("Entry price and stop loss cannot be the same")
        
        # Calculate raw position size
        raw_size = risk_amount / risk_per_unit
        
        # Get instrument info to get contract value
        spec = self.get_instrument_info(symbol)
        contract_value = spec.get('contractValue', 1.0)
        
        # Convert to contracts if needed (divide by contractValue)
        # For example, 1000BONK has contractValue=1000, so 92869 BONK = 92.869 contracts
        raw_contracts = raw_size / contract_value
        
        # Round to lot size (in contracts)
        rounded_size = self.round_size_to_lot(symbol, raw_contracts)
        
        # Calculate actual notional value (contracts * contractValue * price)
        actual_tokens = rounded_size * contract_value
        notional = actual_tokens * entry_price
        
        # Use specified leverage (default 10x for more available margin)
        margin_needed = notional / leverage
        
        return {
            'size': rounded_size,
            'raw_size': raw_size,
            'raw_contracts': raw_contracts,
            'contract_value': contract_value,
            'actual_tokens': actual_tokens,
            'notional_value': notional,
            'margin_needed': margin_needed,
            'leverage': leverage,
            'risk_amount': risk_amount,
            'risk_percent': risk_percent,
            'total_equity': equity,
            'available_balance': available,
            'risk_per_unit': risk_per_unit
        }
    
    def get_instrument_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get instrument specifications (min size, lot size, etc.)
        Cached to avoid repeated API calls.
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            
        Returns:
            Instrument specification dict with minSize, lotSize, etc.
        """
        # Check cache first
        if symbol in self._instrument_cache:
            return self._instrument_cache[symbol]
        
        try:
            instruments = self._request("GET", "/api/v1/market/instruments", {"instType": "SWAP"})
            
            for inst in instruments:
                if inst.get('instId') == symbol:
                    spec = {
                        'minSize': float(inst.get('minSize', 1)),
                        'lotSize': float(inst.get('lotSize', 1)),
                        'tickSize': float(inst.get('tickSize', 0.01)),
                        'contractValue': float(inst.get('contractValue', 1)),
                        'contractType': inst.get('contractType'),
                        'instId': symbol
                    }
                    # Cache it
                    self._instrument_cache[symbol] = spec
                    logger.info(f"Instrument {symbol}: minSize={spec['minSize']}, lotSize={spec['lotSize']}, contractValue={spec['contractValue']}")
                    return spec
            
            # Not found, return defaults
            logger.warning(f"Instrument {symbol} not found, using defaults")
            return {'minSize': 1.0, 'lotSize': 1.0, 'tickSize': 0.01, 'contractValue': 1.0, 'instId': symbol}
            
        except Exception as e:
            logger.warning(f"Failed to get instrument info for {symbol}: {e}, using defaults")
            return {'minSize': 1.0, 'lotSize': 1.0, 'tickSize': 0.01, 'contractValue': 1.0, 'instId': symbol}
    
    def round_size_to_lot(self, symbol: str, size: float) -> float:
        """
        Round position size according to instrument lot size.
        
        Args:
            symbol: Trading pair
            size: Desired position size
            
        Returns:
            Rounded size that meets lot size requirements
        """
        spec = self.get_instrument_info(symbol)
        lot_size = spec['lotSize']
        min_size = spec['minSize']
        
        # Round to nearest lot size increment
        rounded = round(size / lot_size) * lot_size
        
        # Ensure minimum size - if below minimum, FAIL (don't auto-bump)
        if rounded < min_size:
            logger.error(f"❌ Position size {size} below minimum {min_size} for {symbol}")
            raise ValueError(f"Position size {size} is below exchange minimum {min_size} for {symbol}. Increase risk amount or choose a different symbol.")
        
        # For lot sizes >= 1, return as integer
        if lot_size >= 1:
            return int(rounded)
        
        # Otherwise round to appropriate decimal places
        decimals = len(str(lot_size).split('.')[-1]) if '.' in str(lot_size) else 0
        return round(rounded, decimals)
    
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
        
        # Round size according to instrument specifications
        rounded_size = self.round_size_to_lot(symbol, size)
        
        payload = {
            "instId": symbol,
            "marginMode": trade_mode,
            "positionSide": "net",  # Required: net for One-way Mode, long/short for Hedge Mode
            "side": api_side,
            "orderType": "market",
            "size": str(rounded_size)
        }
        
        logger.info(f"Placing market order: {api_side} {rounded_size} {symbol} (requested: {size})")
        
        try:
            response = self._request("POST", "/api/v1/copytrading/trade/place-order", payload)
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
        
        # Round size according to instrument specifications
        rounded_size = self.round_size_to_lot(symbol, size)
        
        payload = {
            "instId": symbol,
            "marginMode": trade_mode,
            "positionSide": "net",  # Required: net for One-way Mode, long/short for Hedge Mode
            "side": api_side,
            "orderType": "limit",
            "size": str(rounded_size),
            "price": str(price)
        }
        
        logger.info(f"Placing limit order: {api_side} {rounded_size} {symbol} @ {price} (requested: {size})")
        
        try:
            response = self._request("POST", "/api/v1/copytrading/trade/place-order", payload)
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
    
    def set_stop_loss(self, symbol: str, side: str, trigger_price: float, size: float,
                     trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Set stop loss order using algo order endpoint.
        
        Args:
            symbol: Trading pair
            side: Order side (opposite of position)
            trigger_price: Stop loss trigger price
            size: Order size
            trade_mode: cross or isolated
            
        Returns:
            Order response
        """
        # Round size according to instrument specifications
        rounded_size = self.round_size_to_lot(symbol, size)
        
        # TPSL endpoint requires INTEGER contracts (unlike market orders)
        # Round UP to ensure full position coverage
        import math
        rounded_size = math.ceil(rounded_size)
        
        if rounded_size == 0:
            raise ValueError(f"Position size too small for {symbol}: {size} contracts rounds to 0")
        
        # Round trigger price to avoid floating point precision issues
        trigger_price = round(trigger_price, 6)
        
        # Determine positionSide based on the position direction
        # For stop loss, if side is sell, position is long; if side is buy, position is short
        if side.lower() in ["sell", "short"]:
            position_side = "long"
        else:
            position_side = "short"
        
        payload = {
            "instId": symbol,
            "marginMode": trade_mode,
            "positionSide": position_side,  # long or short based on position
            "slTriggerPrice": str(int(trigger_price)),
            "tpTriggerPrice": "",
            "size": str(rounded_size)
        }
        
        logger.info(f"Setting stop loss: {symbol} @ {trigger_price} (size: {rounded_size}, requested: {size})")
        logger.info(f"🔍 SL PAYLOAD: {payload}")
        
        try:
            response = self._request("POST", "/api/v1/copytrading/trade/place-tpsl-by-contract", payload)
            algo_id = response.get('algoId')
            logger.info(f"✅ Stop loss set: {algo_id}")
            return {'order_id': algo_id, 'type': 'stop_loss'}
        
        except Exception as e:
            logger.error(f"❌ Failed to set stop loss: {e}")
            raise
    
    def set_multiple_take_profits(self, symbol: str, side: str, total_size: float,
                                  tp_prices: list, trade_mode: str = "cross") -> list:
        """
        Set multiple take profit orders with position split across them.
        Splits position equally across all provided TP levels.
        
        Args:
            symbol: Trading pair
            side: Order side (buy/sell)
            total_size: Total position size to split
            tp_prices: List of TP prices [tp1, tp2, tp3, ...]
            trade_mode: Trading mode (cross/isolated)
        
        Returns:
            List of order results for each TP
        """
        if not tp_prices:
            return []
        
        # Filter out None values
        tp_prices = [tp for tp in tp_prices if tp is not None]
        if not tp_prices:
            return []
        
        # Split position equally across all TPs
        num_tps = len(tp_prices)
        
        # Split total size evenly across TPs (can be fractional)
        size_per_tp = total_size / num_tps
        
        logger.info(f"Splitting {total_size} contracts across {num_tps} TPs: {size_per_tp} each")
        
        results = []
        for i, tp_price in enumerate(tp_prices, 1):
            tp_size = size_per_tp
            
            try:
                result = self.set_take_profit(
                    symbol=symbol,
                    side=side,
                    size=tp_size,
                    trigger_price=tp_price,
                    trade_mode=trade_mode
                )
                # Add size to result for tracking
                result['size'] = tp_size
                result['tp_level'] = i
                logger.info(f"✅ Take profit {i}/{num_tps} set @ {tp_price} for {tp_size} contracts")
                results.append(result)
            except Exception as e:
                logger.warning(f"⚠️ Failed to set TP{i} @ {tp_price}: {e}")
                results.append({'error': str(e), 'tp_level': i, 'size': tp_size})
        
        return results
    
    def set_take_profit(self, symbol: str, side: str, trigger_price: float, size: float,
                       trade_mode: str = "cross") -> Dict[str, Any]:
        """
        Set take profit order using algo order endpoint.
        
        Args:
            symbol: Trading pair
            side: Order side (opposite of position)
            trigger_price: Take profit trigger price
            size: Order size
            trade_mode: cross or isolated
            
        Returns:
            Order response
        """
        # Round size according to instrument specifications
        rounded_size = self.round_size_to_lot(symbol, size)
        
        # TPSL endpoint requires INTEGER contracts (unlike market orders)
        import math
        rounded_size = math.ceil(rounded_size)
        
        if rounded_size == 0:
            raise ValueError(f"Position size too small for {symbol}: {size} contracts rounds to 0")
        
        # Round trigger price to prevent floating point precision issues
        # BloFin rejects prices like 96424.99999999999
        trigger_price = round(trigger_price, 6)
        
        # Determine positionSide based on the position direction
        # For take profit, if side is sell, position is long; if side is buy, position is short
        if side.lower() in ["sell", "short"]:
            position_side = "long"
        else:
            position_side = "short"
        
        payload = {
            "instId": symbol,
            "marginMode": trade_mode,
            "positionSide": position_side,  # long or short based on position
            "tpTriggerPrice": str(int(trigger_price)),
            "slTriggerPrice": "",
            "size": str(rounded_size)
        }
        
        logger.info(f"Setting take profit: {symbol} @ {trigger_price} (size: {rounded_size}, requested: {size})")
        logger.info(f"🔍 TP PAYLOAD: {payload}")
        
        try:
            response = self._request("POST", "/api/v1/copytrading/trade/place-tpsl-by-contract", payload)
            algo_id = response.get('algoId')
            logger.info(f"✅ Take profit set: {algo_id}")
            return {'order_id': algo_id, 'type': 'take_profit'}
        
        except Exception as e:
            logger.error(f"❌ Failed to set take profit: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market ticker for a symbol.
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            
        Returns:
            Ticker data with current price
        """
        try:
            response = self._request("GET", f"/api/v1/market/ticker?instId={symbol}")
            if response and 'data' in response and len(response['data']) > 0:
                return response['data'][0]
            return {}
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Account balance information
        """
        try:
            response = self._request("GET", "/api/v1/copytrading/account/balance")
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
            response = self._request("GET", "/api/v1/copytrading/account/positions-by-contract")
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
    
    def set_leverage(self, symbol: str, leverage: int, margin_mode: str = "cross") -> Dict[str, Any]:
        """
        Set leverage for a trading pair.
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            leverage: Leverage value (1-125)
            margin_mode: cross or isolated
            
        Returns:
            Response from API
        """
        payload = {
            "instId": symbol,
            "leverage": str(leverage),
            "marginMode": margin_mode
        }
        
        logger.info(f"Setting leverage: {symbol} to {leverage}x ({margin_mode})")
        
        try:
            response = self._request("POST", "/api/v1/copytrading/account/set-leverage", payload)
            logger.info(f"✅ Leverage set to {leverage}x")
            return response
        except Exception as e:
            logger.warning(f"⚠️ Failed to set leverage: {e}")
            # Don't raise - leverage setting failure shouldn't stop the trade
            return {}
    
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
