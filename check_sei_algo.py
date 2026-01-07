"""Check SEI algo orders with correct parameters"""
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# Get pending algo orders with required orderType parameter
try:
    response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
        "instId": "SEI-USDT",
        "orderType": "trigger"
    })
    
    print("SEI-USDT Pending Algo Orders:")
    print(json.dumps(response, indent=2))
    
    if response:
        print("\n" + "=" * 60)
        for order in response:
            print(f"Algo ID: {order.get('algoId')}")
            print(f"  Side: {order.get('side')}")
            print(f"  Size: {order.get('size')}")
            print(f"  Trigger Price: ${order.get('triggerPrice')}")
            print(f"  Order Type: {order.get('orderType')}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
