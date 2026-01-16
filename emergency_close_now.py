#!/usr/bin/env python3
"""Emergency script to close BTC position using BlofinClient"""

import sys
import os
sys.path.append('/opt/hitNetworkAutomation/trading-server')

from blofin_client import BloFinClient

def main():
    print("🚨 EMERGENCY CLOSE: Closing 5.2 BTC-USDT position")
    
    # Load credentials from environment
    api_key = os.getenv('BLOFIN_API_KEY')
    secret_key = os.getenv('BLOFIN_SECRET_KEY')
    passphrase = os.getenv('BLOFIN_PASSPHRASE')
    
    if not all([api_key, secret_key, passphrase]):
        # Try loading from .env file
        env_path = '/opt/hitNetworkAutomation/.env'
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
    
    # First, cancel ALL pending orders using API directly
    print("📋 Canceling all pending orders...")
    try:
        cancel_payload = {
            "instId": "BTC-USDT"
        }
        cancel_result = client._request("POST", "/api/v1/copytrading/trade/cancel-all-orders", cancel_payload)
        print(f"Cancel result: {cancel_result}")
    except Exception as e:
        print(f"Cancel warning (may be no orders): {e}")
    
    # Wait a moment for cancellations to process
    import time
    time.sleep(1)
    
    # Place market SELL order to close LONG position
    print("🔻 Placing market SELL order to close position...")
    result = client.place_market_order(
        symbol="BTC-USDT",
        side="sell",
        size=5.2
    )
    
    print(f"Result: {result}")
    
    if result and result.get('order_id'):
        print(f"✅ Position closed! Order ID: {result['order_id']}")
    else:
        print(f"❌ Failed to close position: {result}")

if __name__ == "__main__":
    main()
