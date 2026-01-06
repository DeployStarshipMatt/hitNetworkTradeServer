import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os
import requests
import hmac
import hashlib
import time
import json
import base64

# Load trading server env
load_dotenv("trading-server/.env")

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')

print(f"Testing BloFin with BASE64 signature encoding")
print(f"API Key: {api_key}")

# Test endpoint
path = "/api/v1/asset/balances"
method = "GET"
url = f"{base_url}{path}"

# Generate signature with base64 encoding
timestamp = str(int(time.time() * 1000))
body_str = ''
message = timestamp + method.upper() + path + body_str

print(f"\nMessage to sign: {message}")

# Try base64 encoding
signature_bytes = hmac.new(
    secret_key.encode('utf-8'),
    message.encode('utf-8'),
    hashlib.sha256
).digest()

signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')

print(f"Signature (base64): {signature_base64}")

# Build headers with base64 signature
headers = {
    'BLOFIN-API-KEY': api_key,
    'BLOFIN-API-SIGN': signature_base64,
    'BLOFIN-API-TIMESTAMP': timestamp,
    'BLOFIN-API-PASSPHRASE': passphrase,
    'Content-Type': 'application/json'
}

# Make request
response = requests.get(url, headers=headers, timeout=10)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    if data.get('code') == '0':
        print("\n✅ SUCCESS! Balance retrieved:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ API Error: {data}")
else:
    print(f"\n❌ HTTP Error {response.status_code}")
