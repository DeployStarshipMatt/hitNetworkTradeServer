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

# Load trading server env
load_dotenv("trading-server/.env")

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')

print(f"Testing BloFin connection to: {base_url}")
print(f"API Key: {api_key}")
print(f"Secret Key: {secret_key[:10]}...")
print(f"Passphrase: {passphrase}")

# Test endpoint
path = "/api/v1/asset/balances"
method = "GET"
url = f"{base_url}{path}"

# Generate signature
timestamp = str(int(time.time() * 1000))
body_str = ''
message = timestamp + method.upper() + path + body_str

print(f"\n=== Signature Generation ===")
print(f"Timestamp: {timestamp}")
print(f"Method: {method}")
print(f"Path: {path}")
print(f"Message to sign: {message}")

signature = hmac.new(
    secret_key.encode('utf-8'),
    message.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Signature: {signature}")

# Build headers
headers = {
    'BLOFIN-API-KEY': api_key,
    'BLOFIN-API-SIGN': signature,
    'BLOFIN-API-TIMESTAMP': timestamp,
    'BLOFIN-API-PASSPHRASE': passphrase,
    'Content-Type': 'application/json'
}

print(f"\n=== Request Headers ===")
for key, value in headers.items():
    if 'SIGN' in key:
        print(f"{key}: {value[:20]}...")
    else:
        print(f"{key}: {value}")

# Make request
print(f"\n=== Making Request ===")
print(f"URL: {url}")

response = requests.get(url, headers=headers, timeout=10)

print(f"\n=== Response ===")
print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body: {response.text}")

try:
    data = response.json()
    print(f"\n=== Parsed Response ===")
    print(json.dumps(data, indent=2))
except:
    print("Could not parse JSON response")
