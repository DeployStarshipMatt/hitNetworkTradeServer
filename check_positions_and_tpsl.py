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
print("CHECKING ALL POSITIONS AND THEIR TP/SL ORDERS")
print("=" * 60)

# Get all positions
try:
    positions = client._request("GET", "/api/v1/account/positions")
    
    if positions and isinstance(positions, list):
        print(f"\nFound {len(positions)} open positions:\n")
        
        for pos in positions:
            inst_id = pos.get('instId')
            size = pos.get('positions')
            entry = pos.get('averagePrice')
            mark = pos.get('markPrice')
            pnl = pos.get('unrealizedPnl')
            pnl_pct = pos.get('unrealizedPnlRatio')
            
            side = "LONG" if float(size) > 0 else "SHORT"
            pnl_num = float(pnl)
            pnl_pct_num = float(pnl_pct) * 100
            
            print(f"{inst_id} - {side} {abs(float(size))} contracts")
            print(f"  Entry: ${entry} | Mark: ${mark}")
            print(f"  PnL: ${pnl_num:+.2f} ({pnl_pct_num:+.2f}%)")
            
            # Check for TP/SL orders for this instrument
            try:
                # Try regular account first
                algo_orders = client._request("GET", "/api/v1/trade/orders-algo-pending", {
                    "instId": inst_id
                })
                
                if algo_orders and len(algo_orders) > 0:
                    print(f"  ✅ Has {len(algo_orders)} TP/SL order(s):")
                    for order in algo_orders:
                        order_type = order.get('orderType')
                        trigger = order.get('triggerPrice')
                        print(f"     - {order_type}: ${trigger}")
                else:
                    print(f"  ❌ NO TP/SL PROTECTION")
            except Exception as e:
                print(f"  ⚠️  Could not check TP/SL: {e}")
            
            print()
            
except Exception as e:
    print(f"Error getting positions: {e}")

print("=" * 60)
print("\nSUMMARY:")
print("These are ACTIVE POSITIONS from previous signals.")
print("Check which ones lack TP/SL protection and close or protect them.")
print("=" * 60)
