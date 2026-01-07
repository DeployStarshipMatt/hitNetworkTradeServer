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

# Get all ATOM algo orders
response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
    "instId": "ATOM-USDT",
    "orderType": "trigger"
})

print("All ATOM algo orders:")
for order in response:
    print(f"  {order['algoId']}: {order['side']} {order['size']} @ ${order['triggerPrice']}")

print("\nCanceling ALL algo orders...")
for order in response:
    try:
        result = client._request("POST", "/api/v1/trade/cancel-algo", {
            "instId": "ATOM-USDT",
            "algoId": order['algoId']
        })
        print(f"  Canceled {order['algoId']}")
    except Exception as e:
        print(f"  Error: {e}")

# Now set clean orders
print("\nSetting clean SL/TP:")

# Stop Loss: 3 ATOM @ $2.546
print("  SL: 3 ATOM @ $2.546")
sl_result = client.set_stop_loss("ATOM-USDT", "buy", 2.546, 3)
print(f"    {sl_result['order_id']}")

# TP1: 1 ATOM @ $2.354262
print("  TP1: 1 ATOM @ $2.354262")
tp1_result = client.set_take_profit("ATOM-USDT", "buy", 2.354262, 1)
print(f"    {tp1_result['order_id']}")

# TP2: 1 ATOM @ $2.281054
print("  TP2: 1 ATOM @ $2.281054")
tp2_result = client.set_take_profit("ATOM-USDT", "buy", 2.281054, 1)
print(f"    {tp2_result['order_id']}")

# TP3: 1 ATOM @ $2.217308
print("  TP3: 1 ATOM @ $2.217308")
tp3_result = client.set_take_profit("ATOM-USDT", "buy", 2.217308, 1)
print(f"    {tp3_result['order_id']}")

print("\nDone!")
