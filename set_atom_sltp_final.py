"""
Set stop loss and take profit using algo (trigger) orders
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

print("Setting stop loss and take profit using algo orders...")

# For a SHORT position:
# - Stop loss: trigger BUY when price rises to SL level
# - Take profit: trigger BUY when price falls to TP level

try:
    # Set stop loss using algo order
    print(f"\n🛡️ Setting stop loss at {STOP_LOSS}...")
    sl_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "size": str(POSITION_SIZE),
        "orderType": "trigger",
        "orderPrice": "-1",  # Market price execution
        "triggerPrice": str(STOP_LOSS),
        "triggerPriceType": "mark",  # Use mark price
        "reduceOnly": "true"
    }
    
    sl_response = client._request("POST", "/api/v1/trade/order-algo", sl_payload)
    print(f"✅ Stop loss set: {sl_response}")
    
except Exception as e:
    print(f"❌ Failed to set stop loss: {e}")

try:
    # Set take profit using algo order
    print(f"\n💰 Setting take profit at {TAKE_PROFIT}...")
    tp_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",  # Close short position
        "size": str(POSITION_SIZE),
        "orderType": "trigger",
        "orderPrice": "-1",  # Market price execution
        "triggerPrice": str(TAKE_PROFIT),
        "triggerPriceType": "mark",  # Use mark price
        "reduceOnly": "true"
    }
    
    tp_response = client._request("POST", "/api/v1/trade/order-algo", tp_payload)
    print(f"✅ Take profit set: {tp_response}")
    
except Exception as e:
    print(f"❌ Failed to set take profit: {e}")

print("\n✅ Done!")
print("\nAlgo trigger orders placed:")
print(f" - Stop loss: Triggers at ${STOP_LOSS} (closes with market order)")  
print(f" - Take profit: Triggers at ${TAKE_PROFIT} (closes with market order)")
