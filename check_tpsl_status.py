#!/usr/bin/env python3
import sys
import os
import json
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("CHECKING FOR TP/SL ORDERS")
print("=" * 60)

# Get current positions
positions = client._request("GET", "/api/v1/copytrading/account/positions-by-contract")

for pos in positions:
    inst_id = pos.get('instId')
    contracts = pos.get('positions')
    
    print(f"\n{inst_id} - {contracts} contracts")
    print("-" * 40)
    
    # Check for algo/trigger orders on this symbol
    try:
        # Try copytrading algo pending orders
        algo_orders = client._request("GET", "/api/v1/copytrading/trade/orders-tpsl-pending", {
            "instId": inst_id
        })
        
        print(f"TP/SL Orders: {json.dumps(algo_orders, indent=2)}")
        
        if algo_orders and isinstance(algo_orders, list) and len(algo_orders) > 0:
            for order in algo_orders:
                order_type = order.get('orderType', order.get('side'))
                trigger = order.get('triggerPrice')
                size = order.get('size')
                print(f"  ✅ {order_type}: Trigger @ ${trigger}, Size: {size}")
        else:
            print(f"  ❌ No TP/SL orders found")
            
    except Exception as e:
        print(f"  ⚠️  Error checking TP/SL: {e}")

print("\n" + "=" * 60)
