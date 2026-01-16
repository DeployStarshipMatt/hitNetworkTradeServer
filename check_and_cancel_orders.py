#!/usr/bin/env python3
"""Check pending orders and cancel them individually"""

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
    
    # Check pending orders
    print("📋 Checking pending orders...")
    try:
        # Get pending orders using regular trade endpoint
        orders = client._request("GET", "/api/v1/trade/orders-pending", {"instId": "BTC-USDT"})
        print(f"Pending orders: {orders}")
        
        if orders and isinstance(orders, list):
            for order in orders:
                order_id = order.get('orderId')
                print(f"Found order: {order_id} - {order.get('side')} {order.get('size')} @ {order.get('price')}")
                
                # Cancel this order
                print(f"Canceling order {order_id}...")
                cancel_result = client._request("POST", "/api/v1/trade/cancel-order", {
                    "instId": "BTC-USDT",
                    "orderId": order_id
                })
                print(f"Canceled: {cancel_result}")
    except Exception as e:
        print(f"Error checking orders: {e}")

if __name__ == "__main__":
    main()
