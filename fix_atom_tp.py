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

# Cancel wrong TPs
wrong_tp_ids = ["10002568781", "10002568782", "10002568783"]

print("Canceling wrong take profit orders...")
for tp_id in wrong_tp_ids:
    try:
        result = client._request("POST", "/api/v1/trade/cancel-algo", {
            "instId": "ATOM-USDT",
            "algoId": tp_id
        })
        print(f"  Canceled {tp_id}: {result.get('code')}")
    except Exception as e:
        print(f"  Error canceling {tp_id}: {e}")

# Set correct TPs from signal
tp1 = 2.354262
tp2 = 2.281054
tp3 = 2.217308

print("\nSetting CORRECT take profits:")

# TP1: 1 ATOM @ $2.354262
print(f"  TP1: 1 ATOM @ ${tp1}")
tp1_result = client.set_take_profit("ATOM-USDT", "buy", tp1, 1)
print(f"    Result: {tp1_result['order_id']}")

# TP2: 1 ATOM @ $2.281054
print(f"  TP2: 1 ATOM @ ${tp2}")
tp2_result = client.set_take_profit("ATOM-USDT", "buy", tp2, 1)
print(f"    Result: {tp2_result['order_id']}")

# TP3: 1 ATOM @ $2.217308
print(f"  TP3: 1 ATOM @ ${tp3}")
tp3_result = client.set_take_profit("ATOM-USDT", "buy", tp3, 1)
print(f"    Result: {tp3_result['order_id']}")

print("\nDone! Verifying...")

# Verify
response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
    "instId": "ATOM-USDT",
    "orderType": "trigger"
})

print("\nFinal ATOM algo orders:")
for order in response:
    trigger = float(order.get('triggerPrice'))
    if trigger > 2.5:
        print(f"  STOP LOSS: ${trigger:.6f} ({order.get('size')} ATOM)")
    else:
        print(f"  TAKE PROFIT: ${trigger:.6f} ({order.get('size')} ATOM)")
