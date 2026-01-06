"""
BloFin API Authentication Module

Handles HMAC-SHA256 signature generation and API requests.
Self-contained - can be used independently or with different exchanges.
"""

import hmac
import hashlib
import time
import json
import base64
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BloFinAuth:
    """
    BloFin API authentication and request signing.
    
    Generates required headers for authenticated requests.
    """
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        """
        Initialize BloFin authentication.
        
        Args:
            api_key: BloFin API key
            secret_key: BloFin secret key
            passphrase: BloFin passphrase
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
    
    def generate_signature(self, method: str, path: str, timestamp: str, nonce: str, body: str = '', query: str = '') -> str:
        """
        Generate Blofin-compliant HMAC-SHA256 signature (hex digest, then base64 encoded).
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (no query for POST, with query for GET)
            timestamp: Timestamp in milliseconds (as string)
            nonce: Unique string (UUID)
            body: Request body as JSON string (empty for GET)
            query: Query string (for GET requests)
        Returns:
            Base64-encoded signature string (hex digest)
        """
        prehash = f"{path}{method.upper()}{timestamp}{nonce}{body}"
        hex_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            prehash.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().encode('utf-8')
        signature = base64.b64encode(hex_signature).decode('utf-8')
        return signature
    
    def get_headers(self, method: str, path: str, body: Optional[Dict] = None, params: Optional[Dict] = None, debug: bool = False) -> Dict[str, str]:
        """
        Get authentication headers for request (Blofin-compliant).
        Args:
            method: HTTP method
            path: Request path (no query for POST, with query for GET)
            body: Request body dictionary (will be JSON encoded)
            params: Query parameters (for GET)
        Returns:
            Dictionary of headers
        """
        import uuid
        from urllib.parse import urlencode
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        if method.upper() == 'POST':
            # Sort keys to match Blofin docs order for POST
            doc_order = ["instId", "marginMode", "positionSide", "side", "orderType", "price", "size", "leverage"]
            if body:
                sorted_body = {k: body[k] for k in doc_order if k in body}
                # Add any extra keys at the end
                for k in body:
                    if k not in sorted_body:
                        sorted_body[k] = body[k]
            else:
                sorted_body = None
            body_str = json.dumps(sorted_body, separators=(",", ":")) if sorted_body else ''
            sig_path = path.rstrip('/')  # POST: path only, no trailing slash
        else:
            body_str = ''
            # GET: path includes query string if present
            if params:
                query = urlencode(params)
                sig_path = f"{path.rstrip('/')}?{query}"
            else:
                sig_path = path.rstrip('/')
        signature = self.generate_signature(method, sig_path, timestamp, nonce, body_str)
        if debug:
            print("\n=== BloFin Signature & Header Debug ===")
            print(f"Method: {method}")
            print(f"Path: {sig_path}")
            print(f"Timestamp: {timestamp}")
            print(f"Nonce: {nonce}")
            print(f"Body: {body_str}")
            print(f"Prehash string: '{sig_path}{method.upper()}{timestamp}{nonce}{body_str}'")
            print(f"Signature (base64-hex): {signature}")
            print("Headers:")
            for k, v in {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': signature,
                'ACCESS-TIMESTAMP': timestamp,
                'ACCESS-NONCE': nonce,
                'ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json'
            }.items():
                print(f"  {k}: {v}")
            print("\n=== END DEBUG BLOCK ===\n")
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-NONCE': nonce,
            'ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        return headers
    
    def validate_credentials(self) -> bool:
        """
        Check if credentials are set.
        
        Returns:
            True if all credentials are present
        """
        return bool(self.api_key and self.secret_key and self.passphrase)


if __name__ == "__main__":
    # Test authentication
    auth = BloFinAuth(
        api_key="test_key",
        secret_key="test_secret",
        passphrase="test_pass"
    )
    
    # Generate sample headers
    headers = auth.get_headers(
        method="POST",
        path="/api/v1/private/order",
        body={"inst_id": "BTC-USDT", "side": "buy"}
    )
    
    print("Sample headers:")
    for key, value in headers.items():
        print(f"  {key}: {value[:50]}..." if len(value) > 50 else f"  {key}: {value}")
