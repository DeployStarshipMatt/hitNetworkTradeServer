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
print("ADDING TP/SL TO ALL UNPROTECTED POSITIONS")
print("=" * 60)

# Get all positions - try different endpoints
try:
    positions = client._request("GET", "/api/v1/account/positions")
except:
    try:
        positions = client._request("GET", "/api/v1/copytrading/trade/positions")
    except:
        positions = client._request("GET", "/api/v1/trade/positions")

if not positions or not isinstance(positions, list) or len(positions) == 0:
    print("No positions found")
    exit(0)

print(f"Found {len(positions)} positions to protect\n")

for pos in positions:
    inst_id = pos.get('instId')
    size = float(pos.get('positions', 0))
    entry = float(pos.get('averagePrice'))
    mark = float(pos.get('markPrice'))
    
    if size == 0:
        continue
    
    side = "long" if size > 0 else "short"
    size_abs = abs(size)
    
    print(f"\n{inst_id} - {side.upper()} {size_abs} contracts")
    print(f"  Entry: ${entry:.6f} | Current: ${mark:.6f}")
    
    # Calculate TP and SL (2% risk, 4% reward as default)
    if side == "long":
        stop_loss = entry * 0.98  # 2% below entry
        take_profit = entry * 1.04  # 4% above entry
    else:
        stop_loss = entry * 1.02  # 2% above entry
        take_profit = entry * 0.96  # 4% below entry
    
    print(f"  Setting SL: ${stop_loss:.6f} | TP: ${take_profit:.6f}")
    
    try:
        # Set stop loss
        sl_result = client.set_stop_loss(
            symbol=inst_id,
            side=side,
            trigger_price=stop_loss,
            size=size_abs
        )
        print(f"  ✅ Stop Loss set: {sl_result}")
        
        # Set take profit
        tp_result = client.set_take_profit(
            symbol=inst_id,
            side=side,
            trigger_price=take_profit,
            size=size_abs
        )
        print(f"  ✅ Take Profit set: {tp_result}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("DONE - All positions now have TP/SL protection")
print("=" * 60)
