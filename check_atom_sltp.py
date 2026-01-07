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

# Get ATOM position
positions = client.get_positions()
atom_pos = [p for p in positions if p['instId'] == 'ATOM-USDT']

if atom_pos:
    p = atom_pos[0]
    print(f"ATOM-USDT Position:")
    print(f"  Size: {p['positions']} (SHORT)")
    print(f"  Entry: ${p['averagePrice']}")
    print(f"  Current Price: ${p['markPrice']}")
    print(f"  Unrealized PnL: ${p['unrealizedPnl']}")
    print(f"  Leverage: {p['leverage']}x")
    print()

# Get ATOM algo orders
print("ATOM-USDT Algo Orders:")
try:
    response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
        "instId": "ATOM-USDT",
        "orderType": "trigger"
    })
    
    if response:
        for order in response:
            order_type = "STOP LOSS" if float(order.get('triggerPrice')) > float(atom_pos[0]['averagePrice']) else "TAKE PROFIT"
            print(f"\n{order_type}:")
            print(f"  Algo ID: {order.get('algoId')}")
            print(f"  Side: {order.get('side')}")
            print(f"  Size: {order.get('size')}")
            print(f"  Trigger Price: ${order.get('triggerPrice')}")
    else:
        print("  No algo orders found")
        
except Exception as e:
    print(f"  Error: {e}")
