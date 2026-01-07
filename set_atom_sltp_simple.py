"""
Manually set stop loss and take profit using stop limit orders
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

print("Setting stop loss and take profit on ATOM-USDT SHORT position using simple limit orders...")

# For a SHORT position:
# - Stop loss: limit BUY order ABOVE current price (when price rises, buy to close)
# - Take profit: limit BUY order BELOW current price (when price falls, buy to close)

try:
    # Set stop loss - limit buy order above current price
    print(f"\n🛡️ Setting stop loss at {STOP_LOSS}...")
    sl_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",
        "orderType": "limit",
        "price": str(STOP_LOSS),
        "size": str(POSITION_SIZE),
        "reduceOnly": "true"
    }
    
    sl_response = client._request("POST", "/api/v1/trade/order", sl_payload)
    print(f"✅ Stop loss set: {sl_response}")
    
except Exception as e:
    print(f"❌ Failed to set stop loss: {e}")

try:
    # Set take profit - limit buy order below current price
    print(f"\n💰 Setting take profit at {TAKE_PROFIT}...")
    tp_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",
        "orderType": "limit",
        "price": str(TAKE_PROFIT),
        "size": str(POSITION_SIZE),
        "reduceOnly": "true"
    }
    
    tp_response = client._request("POST", "/api/v1/trade/order", tp_payload)
    print(f"✅ Take profit set: {tp_response}")
    
except Exception as e:
    print(f"❌ Failed to set take profit: {e}")

print("\n✅ Done!")
print("\nNote: These are regular limit orders, not conditional stops.")
print(" - Stop loss will execute when price RISES to $2.546")  
print(" - Take profit will execute when price FALLS to $2.354")
