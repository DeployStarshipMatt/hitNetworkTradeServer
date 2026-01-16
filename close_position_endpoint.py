#!/usr/bin/env python3
"""Close position using copytrading close-position endpoint"""

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
    
    print("🚨 EMERGENCY CLOSE: Using close-position endpoint")
    
    # Try close-position endpoint
    close_payload = {
        "instId": "BTC-USDT",
        "marginMode": "cross",
        "positionSide": "net"
    }
    
    try:
        result = client._request("POST", "/api/v1/copytrading/trade/close-position", close_payload)
        print(f"✅ Position closed! Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main()
