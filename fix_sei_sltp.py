"""Cancel bad algo orders and set correct SL/TP"""
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

# Cancel the bad algo orders
bad_algo_ids = ["10002575594", "10002575596"]

print("Canceling bad algo orders...")
for algo_id in bad_algo_ids:
    try:
        response = client._request("POST", "/api/v1/trade/cancel-algo", {
            "instId": "SEI-USDT",
            "algoId": algo_id
        })
        print(f"Canceled {algo_id}: {response}")
    except Exception as e:
        print(f"Error canceling {algo_id}: {e}")

print("\nSetting correct SL/TP...")

# Correct parameters
size = 1
stop_loss = 0.127698
tp1 = 0.123615

# Stop Loss - CORRECT ORDER: symbol, side, SIZE, TRIGGER_PRICE
print(f"\nStop Loss: 1 SEI @ ${stop_loss}")
sl_result = client.set_stop_loss("SEI-USDT", "buy", size, stop_loss)
print(f"Result: {sl_result}")

# Take Profit - CORRECT ORDER: symbol, side, SIZE, TRIGGER_PRICE  
print(f"\nTake Profit: 1 SEI @ ${tp1}")
tp_result = client.set_take_profit("SEI-USDT", "buy", size, tp1)
print(f"Result: {tp_result}")

print("\n✅ Done! Verifying...")

# Verify
response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
    "instId": "SEI-USDT",
    "orderType": "trigger"
})

for order in response:
    print(f"\nAlgo ID: {order.get('algoId')}")
    print(f"  Side: {order.get('side')}, Size: {order.get('size')}")
    print(f"  Trigger Price: ${order.get('triggerPrice')}")
