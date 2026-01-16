#!/usr/bin/env python3
import sys
import os
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
print("CHECKING ALL ORDERS - CANCELING ONLY BTC")
print("=" * 60)

# Check regular trading account
print("\n1. REGULAR TRADING ACCOUNT - PENDING ORDERS")
print("-" * 60)
try:
    pending = client.get_pending_orders()
    print(f"All pending orders: {pending}")
    
    if pending and len(pending) > 0:
        for order in pending:
            order_id = order.get('orderId')
            inst_id = order.get('instId')
            if inst_id and 'BTC' in inst_id:
                print(f"\n  ⚠️  BTC order found: {order_id} for {inst_id}")
                print(f"  Canceling...")
                cancel_result = client._request("POST", "/api/v1/trade/cancel-order", {
                    "instId": inst_id,
                    "orderId": order_id
                })
                print(f"  Result: {cancel_result}")
            else:
                print(f"  ✓ Keeping {inst_id} order {order_id} (not BTC)")
    else:
        print("No pending orders found.")
except Exception as e:
    print(f"Error: {e}")

# Check copytrading account
print("\n2. COPYTRADING ACCOUNT - PENDING ORDERS")
print("-" * 60)
try:
    pending_ct = client._request("GET", "/api/v1/copytrading/trade/orders-pending")
    print(f"All pending orders: {pending_ct}")
    
    if pending_ct and isinstance(pending_ct, list) and len(pending_ct) > 0:
        for order in pending_ct:
            order_id = order.get('orderId')
            inst_id = order.get('instId')
            if inst_id and 'BTC' in inst_id:
                print(f"\n  ⚠️  BTC order found: {order_id} for {inst_id}")
                print(f"  Canceling...")
                cancel_result = client._request("POST", "/api/v1/copytrading/trade/cancel-order", {
                    "instId": inst_id,
                    "orderId": order_id
                })
                print(f"  Result: {cancel_result}")
            else:
                print(f"  ✓ Keeping {inst_id} order {order_id} (not BTC)")
    else:
        print("No pending orders found.")
except Exception as e:
    print(f"Error: {e}")

# Check positions
print("\n3. CURRENT POSITIONS")
print("-" * 60)
try:
    positions_ct = client._request("GET", "/api/v1/copytrading/trade/positions")
    print(f"Copytrading positions: {positions_ct}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("DONE - Only BTC orders canceled, XLM trade preserved")
print("=" * 60)
