"""
Get trade history to see the BTC trade details
"""
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Get trade history
print("Fetching trade history...\n")
try:
    trades = client._request("GET", "/api/v1/trade/fills", {"instType": "SWAP"})
except:
    print("Fills endpoint failed, trying orders-history instead...\n")
    trades = []

print(f"Found {len(trades)} trades:\n")
print("="*80)

for i, trade in enumerate(trades, 1):
    inst_id = trade.get('instId')
    side = trade.get('side')
    size = trade.get('fillSize')
    price = trade.get('fillPrice')
    timestamp = trade.get('timestamp')
    order_id = trade.get('orderId')
    fee = trade.get('fee')
    
    # Convert timestamp
    if timestamp:
        dt = datetime.fromtimestamp(int(timestamp) / 1000)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        time_str = 'N/A'
    
    print(f"Trade #{i}:")
    print(f"  Symbol: {inst_id}")
    print(f"  Side: {side}")
    print(f"  Size: {size} contracts")
    print(f"  Price: ${price}")
    
    # Calculate notional value
    if size and price:
        notional = float(size) * float(price)
        print(f"  Notional Value: ${notional:.2f}")
    
    print(f"  Fee: {fee}")
    print(f"  Time: {time_str}")
    print(f"  Order ID: {order_id}")
    print("-" * 80)

# Also check order history
print("\n\nOrder History:")
print("="*80)

orders = client._request("GET", "/api/v1/trade/orders-history", {"instType": "SWAP"})

for i, order in enumerate(orders[:10], 1):  # Show last 10 orders
    inst_id = order.get('instId')
    side = order.get('side')
    size = order.get('size')
    price = order.get('price')
    order_type = order.get('orderType')
    state = order.get('state')
    timestamp = order.get('createTime')
    
    if timestamp:
        dt = datetime.fromtimestamp(int(timestamp) / 1000)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        time_str = 'N/A'
    
    print(f"Order #{i}:")
    print(f"  Symbol: {inst_id}")
    print(f"  Side: {side}")
    print(f"  Size: {size} contracts")
    print(f"  Price: ${price}")
    print(f"  Type: {order_type}")
    print(f"  State: {state}")
    print(f"  Time: {time_str}")
    
    if size and price and price != '0':
        notional = float(size) * float(price)
        print(f"  Notional Value: ${notional:.2f}")
    
    print("-" * 80)
