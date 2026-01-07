"""Execute SEI/USDT SHORT trade #1131"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

# Trade details from signal
symbol = "SEI-USDT"
side = "sell"  # SHORT
entry = 0.125294
stop_loss = 0.127698
tp1 = 0.123615
tp2 = 0.121812
tp3 = 0.12017
leverage = 35

# Initialize client
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("SEI/USDT SHORT TRADE #1131")
print("=" * 60)

# Get account balance
balance = client.get_account_balance()
if balance and 'data' in balance and balance['data']:
    available = float(balance['data'][0].get('availableBalance', 0))
    print(f"Available Balance: ${available:.2f} USDT")
else:
    print("⚠️  Could not fetch balance")
    available = 50.44

# Calculate position size for 1% risk
risk_amount = available * 0.01
risk_per_sei = stop_loss - entry
position_size = risk_amount / risk_per_sei

print(f"\n📊 Position Calculation:")
print(f"   Risk Amount: ${risk_amount:.4f} (1% of ${available:.2f})")
print(f"   Risk per SEI: ${risk_per_sei:.6f}")
print(f"   Calculated Size: {position_size:.2f} SEI")

# Get instrument specs and round size
info = client.get_instrument_info(symbol)
if info:
    min_size = float(info.get('minSize', 1))
    lot_size = float(info.get('lotSize', 1))
    print(f"   Min Size: {min_size}, Lot Size: {lot_size}")
    
    rounded_size = client.round_size_to_lot(symbol, position_size)
    print(f"   Rounded Size: {rounded_size} SEI")
else:
    rounded_size = int(position_size)
    print(f"   Rounded Size: {rounded_size} SEI (fallback)")

print(f"\n📝 Trade Details:")
print(f"   Symbol: {symbol}")
print(f"   Side: {side.upper()}")
print(f"   Size: {rounded_size} SEI")
print(f"   Entry: ${entry}")
print(f"   Stop Loss: ${stop_loss}")
print(f"   TP1: ${tp1}")
print(f"   TP2: ${tp2}")
print(f"   TP3: ${tp3}")
print(f"   Leverage: {leverage}x")

# Place market order
print(f"\n🚀 Placing market order...")
order = client.place_market_order(
    symbol=symbol,
    side=side,
    size=rounded_size
)

if order and order.get('code') == '0':
    order_id = order['data'][0].get('orderId')
    print(f"✅ Order placed successfully! Order ID: {order_id}")
    
    # Set stop loss
    print(f"\n🛑 Setting stop loss at ${stop_loss}...")
    sl_result = client.set_stop_loss(
        symbol=symbol,
        side="buy",  # Opposite side for SHORT
        trigger_price=stop_loss,
        size=rounded_size
    )
    
    if sl_result and sl_result.get('code') == '0':
        sl_id = sl_result['data'][0].get('algoId')
        print(f"✅ Stop loss set! Algo ID: {sl_id}")
    else:
        print(f"❌ Stop loss failed: {sl_result}")
    
    # Set 3-tier take profit
    tp_size = rounded_size / 3
    tp_size_rounded = client.round_size_to_lot(symbol, tp_size)
    
    print(f"\n💰 Setting 3-tier take profit ({tp_size_rounded} SEI each)...")
    
    # TP1
    tp1_result = client.set_take_profit(
        symbol=symbol,
        side="buy",
        trigger_price=tp1,
        size=tp_size_rounded
    )
    if tp1_result and tp1_result.get('code') == '0':
        print(f"✅ TP1 set at ${tp1} - Algo ID: {tp1_result['data'][0].get('algoId')}")
    else:
        print(f"❌ TP1 failed: {tp1_result}")
    
    # TP2
    tp2_result = client.set_take_profit(
        symbol=symbol,
        side="buy",
        trigger_price=tp2,
        size=tp_size_rounded
    )
    if tp2_result and tp2_result.get('code') == '0':
        print(f"✅ TP2 set at ${tp2} - Algo ID: {tp2_result['data'][0].get('algoId')}")
    else:
        print(f"❌ TP2 failed: {tp2_result}")
    
    # TP3 - remaining size
    remaining = rounded_size - (tp_size_rounded * 2)
    tp3_result = client.set_take_profit(
        symbol=symbol,
        side="buy",
        trigger_price=tp3,
        size=remaining
    )
    if tp3_result and tp3_result.get('code') == '0':
        print(f"✅ TP3 set at ${tp3} ({remaining} SEI) - Algo ID: {tp3_result['data'][0].get('algoId')}")
    else:
        print(f"❌ TP3 failed: {tp3_result}")
    
    print("\n" + "=" * 60)
    print("✅ TRADE EXECUTION COMPLETE")
    print("=" * 60)
    
else:
    print(f"❌ Order failed: {order}")
