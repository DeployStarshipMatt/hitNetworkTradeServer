"""
Test BloFin POST with EXACT docs example
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os
import hmac
import hashlib
import base64
import json
import requests
import time
import uuid

# Load trading server env
load_dotenv("trading-server/.env")

api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = "https://openapi.blofin.com"

# Exact docs example payload
path = "/api/v1/trade/order"
method = "POST"
timestamp = str(int(time.time() * 1000))
nonce = str(uuid.uuid4())

body = {
    "instId": "BTC-USDT",
    "marginMode": "isolated",
    "positionSide": "long",
    "side": "sell",
    "orderType": "limit",
    "price": "23212.2",
    "size": "2"
}

body_str = json.dumps(body, separators=(",", ":"))
prehash = f"{path}{method}{timestamp}{nonce}{body_str}"
hex_signature = hmac.new(
    secret_key.encode(),
    prehash.encode(),
    hashlib.sha256
).hexdigest().encode()
signature = base64.b64encode(hex_signature).decode()

headers = {
    'ACCESS-KEY': api_key,
    'ACCESS-SIGN': signature,
    'ACCESS-TIMESTAMP': timestamp,
    'ACCESS-NONCE': nonce,
    'ACCESS-PASSPHRASE': passphrase,
    'Content-Type': 'application/json'
}

print("=== Exact Docs Example Test ===")
print(f"Prehash: {prehash}")
print(f"Signature: {signature}")
print(f"Payload: {body_str}")

response = requests.post(f"{base_url}{path}", headers=headers, json=body, timeout=10)
print(f"\nResponse: {response.status_code}")
print(response.json())

# Try again with data=body_str instead of json=body
print("\n\n=== Retry with data= instead of json= ===")
response2 = requests.post(f"{base_url}{path}", headers=headers, data=body_str, timeout=10)
print(f"Response: {response2.status_code}")
print(response2.json())
