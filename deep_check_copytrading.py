#!/usr/bin/env python3
"""Check copytrading pending orders and position details"""

import sys
import os
import json
sys.path.append('/opt/hitNetworkAutomation/trading-server')

from blofin_client import BloFinClient

def main():
    # Load credentials
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
    
    print("📋 Checking copytrading account state...\n")
    
    # Check copytrading pending orders
    print("1. Pending market orders:")
    try:
        orders = client._request("GET", "/api/v1/copytrading/trade/orders-pending", {"instId": "BTC-USDT"})
        print(json.dumps(orders, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # Check copytrading order history
    print("\n2. Recent order history:")
    try:
        history = client._request("GET", "/api/v1/copytrading/trade/orders-history", {"instId": "BTC-USDT"})
        if history and isinstance(history, list):
            for order in history[:5]:
                print(f"  {order.get('orderId')}: {order.get('side')} {order.get('size')} - {order.get('state')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check specific position with API
    print("\n3. Position data from API:")
    try:
        account = client.get_account_balance()
        print(json.dumps(account, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
