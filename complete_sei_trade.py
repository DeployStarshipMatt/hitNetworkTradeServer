"""Add to SEI position and set SL/TP"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Check current position
positions = client.get_positions()
sei_position = [p for p in positions if p['instId'] == 'SEI-USDT'][0]
current_size = abs(int(sei_position['positions']))
print(f"Current SEI position: {current_size} SHORT")

# We want 140 total, currently have 1 (plus maybe the BTC test)
target_size = 140
additional_size = target_size - current_size

print(f"Target: {target_size} SEI")
print(f"Need to add: {additional_size} SEI")
print()

if additional_size > 0:
    print(f"Adding {additional_size} SEI to position...")
    result = client.place_market_order("SEI-USDT", "sell", additional_size)
    print(f"Result: {result}")
    print()

# Now set SL/TP on full position
stop_loss = 0.127698
tp1 = 0.123615
tp2 = 0.121812
tp3 = 0.12017

print(f"Setting Stop Loss & Take Profit on {target_size} SEI...")

# Stop Loss
print(f"\nStop Loss @ ${stop_loss}...")
sl_result = client.set_stop_loss("SEI-USDT", "buy", stop_loss, target_size)
if sl_result and sl_result.get('code') == '0':
    print(f"✅ SL set! Algo ID: {sl_result['data'][0].get('algoId')}")
else:
    print(f"Result: {sl_result}")

# 3-tier TP
tp_size = target_size // 3  # 46 each
remaining = target_size - (tp_size * 2)  # 48 for TP3

print(f"\n💰 Take Profit:")
print(f"   TP1: {tp_size} SEI @ ${tp1}")
print(f"   TP2: {tp_size} SEI @ ${tp2}")
print(f"   TP3: {remaining} SEI @ ${tp3}")

tp1_result = client.set_take_profit("SEI-USDT", "buy", tp1, tp_size)
if tp1_result and tp1_result.get('code') == '0':
    print(f"✅ TP1 set! Algo ID: {tp1_result['data'][0].get('algoId')}")

tp2_result = client.set_take_profit("SEI-USDT", "buy", tp2, tp_size)
if tp2_result and tp2_result.get('code') == '0':
    print(f"✅ TP2 set! Algo ID: {tp2_result['data'][0].get('algoId')}")

tp3_result = client.set_take_profit("SEI-USDT", "buy", tp3, remaining)
if tp3_result and tp3_result.get('code') == '0':
    print(f"✅ TP3 set! Algo ID: {tp3_result['data'][0].get('algoId')}")

print("\n✅ SEI trade setup complete!")
