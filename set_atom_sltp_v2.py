"""
Set stop loss and take profit on existing ATOM-USDT position using close position trigger orders
"""
import sys
import os
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

# Load environment variables
load_dotenv()

# Initialize client
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Parameters
SYMBOL = "ATOM-USDT"
POSITION_SIZE = 3
STOP_LOSS = 2.545951
TAKE_PROFIT = 2.354262

print("Setting stop loss and take profit on ATOM-USDT SHORT position...")

# For a SHORT position:
# - Stop loss triggers when price goes UP (we need to buy to close at a loss)
# - Take profit triggers when price goes DOWN (we need to buy to close at a profit)

try:
    # Set stop loss - trigger buy when price rises to SL
    print(f"\n🛡️ Setting stop loss at {STOP_LOSS}...")
    sl_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "orderType": "trigger_limit",  # Trigger order
        "size": str(POSITION_SIZE),
        "triggerPrice": str(STOP_LOSS),
        "price": str(STOP_LOSS * 1.01),  # Limit price slightly above trigger
        "triggerPriceType": "mark"  # Use mark price for trigger
    }
    
    sl_response = client._request("POST", "/api/v1/trade/order", sl_payload)
    print(f"✅ Stop loss set: {sl_response}")
    
except Exception as e:
    print(f"❌ Failed to set stop loss: {e}")

try:
    # Set take profit - trigger buy when price falls to TP
    print(f"\n💰 Setting take profit at {TAKE_PROFIT}...")
    tp_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "orderType": "trigger_limit",  # Trigger order
        "size": str(POSITION_SIZE),
        "triggerPrice": str(TAKE_PROFIT),
        "price": str(TAKE_PROFIT * 0.99),  # Limit price slightly below trigger
        "triggerPriceType": "mark"  # Use mark price for trigger
    }
    
    tp_response = client._request("POST", "/api/v1/trade/order", tp_payload)
    print(f"✅ Take profit set: {tp_response}")
    
except Exception as e:
    print(f"❌ Failed to set take profit: {e}")

print("\n✅ Done!")
