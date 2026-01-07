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

# Get SEI position
positions = client.get_positions()
sei_pos = [p for p in positions if p['instId'] == 'SEI-USDT']

if sei_pos:
    p = sei_pos[0]
    print(f"SEI-USDT Position:")
    print(f"  Size: {p['positions']} (SHORT)")
    print(f"  Entry: ${p['averagePrice']}")
    print(f"  Current Price: ${p['markPrice']}")
    print(f"  Unrealized PnL: ${p['unrealizedPnl']}")
    print()

# Get SEI algo orders
print("SEI-USDT Algo Orders:")
try:
    response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
        "instId": "SEI-USDT",
        "orderType": "trigger"
    })
    
    if response:
        for order in response:
            trigger = float(order.get('triggerPrice'))
            if trigger > 0.126:
                print(f"  STOP LOSS: ${trigger:.6f} ({order.get('size')} SEI) - ID: {order.get('algoId')}")
            else:
                print(f"  TAKE PROFIT: ${trigger:.6f} ({order.get('size')} SEI) - ID: {order.get('algoId')}")
    else:
        print("  No algo orders found")
        
except Exception as e:
    print(f"  Error: {e}")

print("\nSignal should be:")
print("  Entry: $0.125294")
print("  SL: $0.127698")
print("  TP1: $0.123615 (1 SEI)")
print("  TP2: $0.121812 (1 SEI)")
print("  TP3: $0.12017 (1 SEI)")
