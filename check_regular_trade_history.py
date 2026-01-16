#!/usr/bin/env python3
"""Check regular trade order history"""

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
    
    print("📋 Checking regular trade order history...")
    
    try:
        # Check regular trade history
        history = client._request("GET", "/api/v1/trade/orders-history", {
            "instId": "BTC-USDT"
        })
        print(f"\nRecent orders: {history}\n")
        
        if history and isinstance(history, list):
            for order in history[:10]:
                print(f"Order {order.get('orderId')}: {order.get('side')} {order.get('size')} @ {order.get('price')} - State: {order.get('state')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
