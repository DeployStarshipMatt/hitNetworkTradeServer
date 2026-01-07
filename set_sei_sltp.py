"""Set SL/TP on existing 1 SEI position"""
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

# Current position
size = 1
stop_loss = 0.127698
tp1 = 0.123615

print(f"Setting SL/TP on {size} SEI SHORT position...")

# Stop Loss
print(f"\nStop Loss @ ${stop_loss}...")
sl_result = client.set_stop_loss("SEI-USDT", "buy", stop_loss, size)
print(f"SL Result: {sl_result}")

# Take Profit  
print(f"\nTake Profit @ ${tp1}...")
tp_result = client.set_take_profit("SEI-USDT", "buy", tp1, size)
print(f"TP Result: {tp_result}")

print("\nDone!")
