"""
Set stop loss and take profit on existing ATOM position
"""
import os
import sys
from dotenv import load_dotenv

sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv('trading-server/.env')

SYMBOL = "ATOM-USDT"
POSITION_SIZE = 3
STOP_LOSS = 2.545951
TAKE_PROFIT = 2.354262

base_url = os.getenv('BLOFIN_BASE_URL')
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')

client = BloFinClient(api_key, secret_key, passphrase, base_url)

print(f"Setting stop loss and take profit on ATOM-USDT SHORT position...")
print()

# Set stop loss
print(f"🛡️ Setting stop loss at {STOP_LOSS}...")
try:
    sl_result = client.set_stop_loss(
        symbol=SYMBOL,
        side="buy",  # Opposite of SHORT
        size=POSITION_SIZE,
        trigger_price=STOP_LOSS,
        trade_mode="cross"
    )
    print(f"✅ Stop loss set: {sl_result}")
except Exception as e:
    print(f"❌ Failed to set stop loss: {e}")

print()

# Set take profit
print(f"💰 Setting take profit at {TAKE_PROFIT}...")
try:
    tp_result = client.set_take_profit(
        symbol=SYMBOL,
        side="buy",  # Opposite of SHORT
        size=POSITION_SIZE,
        trigger_price=TAKE_PROFIT,
        trade_mode="cross"
    )
    print(f"✅ Take profit set: {tp_result}")
except Exception as e:
    print(f"❌ Failed to set take profit: {e}")

print()
print("✅ Done!")
