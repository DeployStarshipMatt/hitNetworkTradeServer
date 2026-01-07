import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# ATOM trade details (from original signal)
entry = 2.414
stop_loss = 2.546  # From the original signal
size = 3

print(f"Setting ATOM Stop Loss...")
print(f"  Entry: ${entry}")
print(f"  Stop Loss: ${stop_loss}")
print(f"  Size: {size} ATOM")
print()

# Set stop loss (buy to close the short)
sl_result = client.set_stop_loss(
    symbol="ATOM-USDT",
    side="buy",
    trigger_price=stop_loss,
    size=size
)

print(f"Stop Loss Set: {sl_result}")
