#!/usr/bin/env python3
import sys
import os
import json
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("SEARCHING FOR TP/SL DATA IN ALL AVAILABLE ENDPOINTS")
print("=" * 60)

symbols = ["CAKE-USDT", "XLM-USDT"]

for symbol in symbols:
    print(f"\n{symbol}:")
    print("-" * 40)
    
    # Try different endpoints
    endpoints = [
        "/api/v1/copytrading/trade/orders-pending",
        "/api/v1/copytrading/trade/orders-algo-pending",
        "/api/v1/copytrading/account/position-tiers"
    ]
    
    for endpoint in endpoints:
        try:
            result = client._request("GET", endpoint, {"instId": symbol})
            print(f"\n  {endpoint}:")
            if result and (isinstance(result, list) and len(result) > 0 or isinstance(result, dict)):
                print(json.dumps(result, indent=4))
            else:
                print(f"    Empty/None")
        except Exception as e:
            print(f"    Error: {e}")

print("\n" + "=" * 60)
print("If TP/SL are set, they should appear in one of these endpoints")
print("=" * 60)
