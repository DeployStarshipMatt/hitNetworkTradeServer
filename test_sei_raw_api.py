"""Place SEI trade with full response logging"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_auth import generate_signature
from dotenv import load_dotenv
import os
import requests
import time
import uuid
import json

load_dotenv()

api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')

# Prepare order
symbol = "SEI-USDT"
size = 140
payload = {
    "instId": symbol,
    "marginMode": "cross",
    "positionSide": "net",
    "side": "sell",
    "orderType": "market",
    "size": str(size)
}

# Generate auth
timestamp = str(int(time.time() * 1000))
nonce = str(uuid.uuid4())
body_str = json.dumps(payload, separators=(',', ':'))
path = "/api/v1/trade/order"
method = "POST"

prehash = f"'{path}{method}{timestamp}{nonce}{body_str}'"
signature = generate_signature(secret_key, prehash)

headers = {
    "ACCESS-KEY": api_key,
    "ACCESS-SIGN": signature,
    "ACCESS-TIMESTAMP": timestamp,
    "ACCESS-NONCE": nonce,
    "ACCESS-PASSPHRASE": passphrase,
    "Content-Type": "application/json"
}

print(f"Placing order: {payload}")
print(f"URL: https://openapi.blofin.com{path}")
print()

# Make request
response = requests.post(
    f"https://openapi.blofin.com{path}",
    headers=headers,
    json=payload
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body: {response.text}")
print()

# Parse response
try:
    data = response.json()
    print(f"Parsed JSON: {json.dumps(data, indent=2)}")
except:
    print("Could not parse JSON")
