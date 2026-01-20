"""
Test: Try to place TP/SL on a position that already has one.
Should get error 200108 if TP/SL truly exists.
"""
import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, 'trading-server')

from blofin_client import BloFinClient

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Try to set TP/SL on CRO (which should already have one)
print("Attempting to place TP/SL on CRO-USDT (already has one)...")
print("Expected: Error 200108 'already a take-profit/stop-loss order'")
print()

try:
    response = client.set_tpsl_pair(
        symbol="CRO-USDT",
        tp_price=0.091207,  # Same as existing
        sl_price=0.095835,  # Same as existing
        size=1060,  # Current position size
        trade_mode="cross"
    )
    print(f"⚠️ UNEXPECTED: Order placed successfully!")
    print(f"Response: {response}")
except Exception as e:
    error_msg = str(e)
    if "200108" in error_msg or "already a take-profit/stop-loss" in error_msg:
        print(f"✅ CONFIRMED: TP/SL order already exists!")
        print(f"Error: {error_msg}")
    else:
        print(f"❌ Different error: {error_msg}")
