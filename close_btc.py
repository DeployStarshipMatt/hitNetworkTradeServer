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

# Check for BTC algo orders
print("Checking BTC algo orders...")
try:
    response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
        "instId": "BTC-USDT",
        "orderType": "trigger"
    })
    
    if response:
        print(f"  Found {len(response)} algo orders:")
        for order in response:
            print(f"    {order['algoId']}: {order['side']} {order['size']} @ ${order['triggerPrice']}")
    else:
        print("  No algo orders set")
except Exception as e:
    print(f"  Error: {e}")

print("\nClosing BTC position (0.1 BTC)...")
try:
    # Sell 0.1 BTC to close the long
    result = client.place_market_order("BTC-USDT", "sell", 0.1)
    print(f"  Position closed: {result}")
except Exception as e:
    print(f"  Error closing: {e}")
