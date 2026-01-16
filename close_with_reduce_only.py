#!/usr/bin/env python3
"""Close BTC position using reduce-only flag"""

import sys
import os
sys.path.append('/opt/hitNetworkAutomation/trading-server')

from blofin_client import BloFinClient

def main():
    # Load credentials from .env
    env_path = '/opt/hitNetworkAutomation/.env'
    api_key = None
    secret_key = None
    passphrase = None
    
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'BLOFIN_API_KEY':
                        api_key = value
                    elif key == 'BLOFIN_SECRET_KEY':
                        secret_key = value
                    elif key == 'BLOFIN_PASSPHRASE':
                        passphrase = value
    
    client = BloFinClient(api_key, secret_key, passphrase)
    
    print("🚨 EMERGENCY CLOSE: Closing BTC position with reduce-only flag")
    
    # Try closing with reduce-only flag
    close_payload = {
        "instId": "BTC-USDT",
        "marginMode": "cross",
        "positionSide": "net",
        "side": "sell",
        "orderType": "market",
        "size": "5.2",
        "reduceOnly": "true"
    }
    
    try:
        result = client._request("POST", "/api/v1/copytrading/trade/place-order", close_payload)
        print(f"✅ Position closed! Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        
        # Try with regular trade endpoint as fallback
        print("\nTrying regular trade endpoint...")
        try:
            result2 = client._request("POST", "/api/v1/trade/order", close_payload)
            print(f"✅ Position closed via regular endpoint! Result: {result2}")
        except Exception as e2:
            print(f"❌ Also failed: {e2}")

if __name__ == "__main__":
    main()
