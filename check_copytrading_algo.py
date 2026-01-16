#!/usr/bin/env python3
"""Check and cancel copytrading algo orders (TPSL)"""

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
    
    print("📋 Checking copytrading algo orders (TPSL)...")
    
    try:
        # Check pending algo orders
        orders = client._request("GET", "/api/v1/copytrading/trade/orders-algo-pending", {
            "instId": "BTC-USDT"
        })
        print(f"\nPending algo orders: {orders}\n")
        
        if orders and isinstance(orders, list):
            for order in orders:
                algo_id = order.get('algoId')
                order_type = order.get('orderType')
                print(f"Found algo order: {algo_id} - Type: {order_type}")
                
                # Cancel this algo order
                print(f"Canceling algo order {algo_id}...")
                cancel_result = client._request("POST", "/api/v1/copytrading/trade/cancel-algo", {
                    "algoId": algo_id,
                    "instId": "BTC-USDT"
                })
                print(f"Canceled: {cancel_result}")
        else:
            print("No pending algo orders found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
