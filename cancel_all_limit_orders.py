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
print("CHECKING AND CANCELING ALL PENDING ORDERS")
print("=" * 60)

# Check regular trading account
print("\n1. REGULAR TRADING ACCOUNT")
print("-" * 60)
try:
    pending = client.get_pending_orders()
    print(f"Pending orders: {pending}")
    
    if pending and len(pending) > 0:
        print(f"\nFound {len(pending)} pending order(s). Canceling...")
        for order in pending:
            order_id = order.get('orderId')
            inst_id = order.get('instId')
            if order_id and inst_id:
                print(f"  Canceling order {order_id} for {inst_id}...")
                cancel_result = client._request("POST", "/api/v1/trade/cancel-order", {
                    "instId": inst_id,
                    "orderId": order_id
                })
                print(f"  Result: {cancel_result}")
    else:
        print("No pending orders found.")
except Exception as e:
    print(f"Error checking regular account: {e}")

# Check copytrading account - pending orders
print("\n2. COPYTRADING ACCOUNT - PENDING ORDERS")
print("-" * 60)
try:
    pending_ct = client._request("GET", "/api/v1/copytrading/trade/orders-pending")
    print(f"Pending orders: {pending_ct}")
    
    if pending_ct and isinstance(pending_ct, list) and len(pending_ct) > 0:
        print(f"\nFound {len(pending_ct)} pending order(s). Canceling...")
        for order in pending_ct:
            order_id = order.get('orderId')
            inst_id = order.get('instId')
            if order_id and inst_id:
                print(f"  Canceling order {order_id} for {inst_id}...")
                cancel_result = client._request("POST", "/api/v1/copytrading/trade/cancel-order", {
                    "instId": inst_id,
                    "orderId": order_id
                })
                print(f"  Result: {cancel_result}")
    else:
        print("No pending orders found.")
except Exception as e:
    print(f"Error checking copytrading pending: {e}")

# Try cancel-all on both accounts
print("\n3. CANCEL-ALL ORDERS (REGULAR)")
print("-" * 60)
try:
    cancel_all_regular = client._request("POST", "/api/v1/trade/cancel-all-orders")
    print(f"Result: {cancel_all_regular}")
except Exception as e:
    print(f"Error: {e}")

print("\n4. CANCEL-ALL ORDERS (COPYTRADING)")
print("-" * 60)
try:
    cancel_all_ct = client._request("POST", "/api/v1/copytrading/trade/cancel-all-orders")
    print(f"Result: {cancel_all_ct}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("DONE - All limit/pending orders canceled")
print("=" * 60)
