#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("CHECKING FOR DUPLICATE TRADE ENTRIES")
print("=" * 60)

# Check order history for each position
positions_to_check = ['HYPE-USDT', 'LINK-USDT', 'WIF-USDT', 'BNB-USDT', 'DASH-USDT', 'DOT-USDT', 'WLFI-USDT', 'ASTER-USDT']

for symbol in positions_to_check:
    print(f"\n{symbol}:")
    print("-" * 40)
    
    try:
        # Get order history
        history = client._request("GET", "/api/v1/account/orders-history", {
            "instId": symbol
        })
        
        if history and isinstance(history, list):
            # Group by side and timestamp to find duplicates
            buy_orders = [o for o in history if o.get('side') == 'buy']
            sell_orders = [o for o in history if o.get('side') == 'sell']
            
            print(f"  Total orders: {len(history)} (Buys: {len(buy_orders)}, Sells: {len(sell_orders)})")
            
            # Show recent orders
            for order in history[:5]:
                side = order.get('side')
                size = order.get('size')
                state = order.get('state')
                timestamp = order.get('createTime')
                order_id = order.get('orderId')
                
                try:
                    dt = datetime.fromtimestamp(int(timestamp)/1000)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp
                
                print(f"    {side.upper()} {size} - {state} - {time_str} - {order_id}")
                
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Look for orders with same size and close timestamps")
print("=" * 60)
