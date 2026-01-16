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
print("CHECKING REGULAR TRADING ACCOUNT")
print("=" * 60)

# Check regular trading account pending orders
print("\nPENDING ORDERS:")
print("-" * 60)
try:
    pending = client._request("GET", "/api/v1/trade/orders-pending")
    print(f"Result: {pending}")
    
    if pending and isinstance(pending, list) and len(pending) > 0:
        print(f"\nFound {len(pending)} pending order(s):")
        for order in pending:
            order_id = order.get('orderId')
            inst_id = order.get('instId')
            side = order.get('side')
            order_type = order.get('orderType')
            size = order.get('size')
            print(f"  - {inst_id}: {side} {size} ({order_type}) - Order ID: {order_id}")
            
            if inst_id and 'BTC' in inst_id:
                print(f"    ⚠️  BTC order - canceling...")
                cancel_result = client._request("POST", "/api/v1/trade/cancel-order", {
                    "instId": inst_id,
                    "orderId": order_id
                })
                print(f"    Result: {cancel_result}")
            else:
                print(f"    ✓ Keeping (not BTC)")
    else:
        print("No pending orders.")
except Exception as e:
    print(f"Error: {e}")

# Check positions
print("\nPOSITIONS:")
print("-" * 60)
try:
    positions = client._request("GET", "/api/v1/trade/positions")
    print(f"Result: {positions}")
    
    if positions and isinstance(positions, list):
        for pos in positions:
            inst_id = pos.get('instId')
            position_side = pos.get('positionSide')
            contracts = pos.get('contracts')
            unrealized_pnl = pos.get('unrealizedPnl')
            print(f"  {inst_id} {position_side}: {contracts} contracts, PnL: {unrealized_pnl}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
