import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os
import json

# Load trading server env
load_dotenv("trading-server/.env")

from blofin_client import BloFinClient
from blofin_auth import BloFinAuth

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')

print(f"Comparing GET and POST signature debug on BloFin: {base_url}")
print(f"API Key: {api_key[:10]}...")

auth = BloFinAuth(api_key, secret_key, passphrase)

# --- GET Example ---
get_path = "/api/v1/account/margin-mode"
get_method = "GET"
get_params = None
get_body = None
print("\n=== GET Signature Debug ===")
headers_get = auth.get_headers(get_method, get_path, body=get_body, params=get_params, debug=True)

# --- POST Example ---
post_path = "/api/v1/trade/order"
post_method = "POST"
post_payload = {
    "instId": "BTC-USDT",
    "marginMode": "cross",
    "side": "buy",
    "orderType": "market",
    "size": "0.1",
    "leverage": "1"
}
print("\n=== POST Signature Debug ===")
headers_post = auth.get_headers(post_method, post_path, body=post_payload, params=None, debug=True)

print("\n=== END OF COMPARISON ===\n")