"""Check algo orders"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get algo orders directly via API
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# Get all pending algo orders
response = client._request("GET", "/api/v1/trade/orders-algo-pending", {"instId": "SEI-USDT"})
print("SEI-USDT Algo Orders:")
import json
print(json.dumps(response, indent=2))
