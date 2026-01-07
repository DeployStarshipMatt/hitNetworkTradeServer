"""
Set stop loss and take profit on existing ATOM-USDT position using reduceOnly limit orders
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
    # Set stop loss using a regular limit order with SL trigger
    print(f"\n🛡️ Setting stop loss at {STOP_LOSS}...")
    sl_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "orderType": "limit",
        "price": str(STOP_LOSS * 1.02),  # Limit price above trigger to ensure execution
        "size": str(POSITION_SIZE),
        "reduceOnly": "true",  # Only close position, don't open new one
        "slTriggerPrice": str(STOP_LOSS),
        "slOrderPrice": str(STOP_LOSS * 1.02)
    }
    
    sl_response = client._request("POST", "/api/v1/trade/order", sl_payload)
    print(f"✅ Stop loss set: {sl_response}")
    
except Exception as e:
    print(f"❌ Failed to set stop loss: {e}")

try:
    # Set take profit using a regular limit order with TP trigger
    print(f"\n💰 Setting take profit at {TAKE_PROFIT}...")
    tp_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "orderType": "limit",
        "price": str(TAKE_PROFIT * 0.98),  # Limit price below trigger to ensure execution
        "size": str(POSITION_SIZE),
        "reduceOnly": "true",  # Only close position, don't open new one
        "tpTriggerPrice": str(TAKE_PROFIT),
        "tpOrderPrice": str(TAKE_PROFIT * 0.98)
    }
    
    tp_response = client._request("POST", "/api/v1/trade/order", tp_payload)
    print(f"✅ Take profit set: {tp_response}")
    
except Exception as e:
    print(f"❌ Failed to take profit: {e}")

print("\n✅ Done!")
