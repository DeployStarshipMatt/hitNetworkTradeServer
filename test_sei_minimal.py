"""Try minimal SEI trade to diagnose issue"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from dotenv import load_dotenv
import os
import requests

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Try placing a very small order
print("Attempting minimal 1 SEI order...")
try:
    order = client.place_market_order(
        symbol="SEI-USDT",
        side="sell",
        size=1
    )
    print(f"Result: {order}")
except Exception as e:
    print(f"Error: {e}")

# Also try BTC which we know works
print("\nAttempting minimal BTC order (0.1 BTC = ~$10k)...")
try:
    order = client.place_market_order(
        symbol="BTC-USDT",
        side="buy",
        size=0.1
    )
    print(f"Result: {order}")
except Exception as e:
    print(f"Error: {e}")
