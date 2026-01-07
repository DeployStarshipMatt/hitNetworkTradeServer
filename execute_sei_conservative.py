"""Execute SEI/USDT SHORT trade with conservative size"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

# Trade details - use smaller size for safety
symbol = "SEI-USDT"
side = "sell"  # SHORT
current_price = 0.1244
stop_loss = 0.127698
tp1 = 0.123615
tp2 = 0.121812
tp3 = 0.12017

# Calculate size for 1% risk with 2x leverage
available = 46.75
risk_amount = available * 0.01  # $0.4675
risk_per_sei = stop_loss - current_price  # 0.003298
size = int(risk_amount / risk_per_sei)  # ~141 SEI

# Round down to safe size
size = 140

# Initialize client
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("SEI/USDT SHORT TRADE #1131")
print("=" * 60)
print(f"Available Balance: ${available:.2f} USDT")
print(f"Risk Amount: ${risk_amount:.4f} (1%)")
print(f"Risk per SEI: ${risk_per_sei:.6f}")
print(f"Position Size: {size} SEI")
print(f"Notional Value: ${size * current_price:.2f}")
print(f"Margin @ 2x: ${(size * current_price) / 2:.2f}")
print()

# Place market order
print(f"🚀 Placing market order for {size} SEI SHORT...")
try:
    order = client.place_market_order(
        symbol=symbol,
        side=side,
        size=size
    )
    
    if order and order.get('code') == '0':
        order_id = order['data'][0].get('orderId')
        print(f"✅ Order placed! Order ID: {order_id}")
        
        # Set stop loss
        print(f"\n🛑 Setting stop loss at ${stop_loss}...")
        sl_result = client.set_stop_loss(
            symbol=symbol,
            side="buy",
            trigger_price=stop_loss,
            size=size
        )
        
        if sl_result and sl_result.get('code') == '0':
            print(f"✅ Stop loss set! Algo ID: {sl_result['data'][0].get('algoId')}")
        else:
            print(f"⚠️  Stop loss result: {sl_result}")
        
        # Set 3-tier TP
        tp_size = size // 3
        remaining = size - (tp_size * 2)
        
        print(f"\n💰 Setting 3-tier take profit:")
        print(f"   TP1: {tp_size} SEI @ ${tp1}")
        print(f"   TP2: {tp_size} SEI @ ${tp2}")
        print(f"   TP3: {remaining} SEI @ ${tp3}")
        
        # TP1
        tp1_result = client.set_take_profit(symbol=symbol, side="buy", trigger_price=tp1, size=tp_size)
        if tp1_result and tp1_result.get('code') == '0':
            print(f"✅ TP1 set - Algo ID: {tp1_result['data'][0].get('algoId')}")
        
        # TP2
        tp2_result = client.set_take_profit(symbol=symbol, side="buy", trigger_price=tp2, size=tp_size)
        if tp2_result and tp2_result.get('code') == '0':
            print(f"✅ TP2 set - Algo ID: {tp2_result['data'][0].get('algoId')}")
        
        # TP3
        tp3_result = client.set_take_profit(symbol=symbol, side="buy", trigger_price=tp3, size=remaining)
        if tp3_result and tp3_result.get('code') == '0':
            print(f"✅ TP3 set - Algo ID: {tp3_result['data'][0].get('algoId')}")
        
        print("\n" + "=" * 60)
        print("✅ TRADE EXECUTION COMPLETE")
        print("=" * 60)
    else:
        print(f"❌ Order failed: {order}")
        
except Exception as e:
    print(f"❌ Error: {e}")
