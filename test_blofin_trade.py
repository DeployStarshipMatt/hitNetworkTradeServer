import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os

# Load trading server env
load_dotenv("trading-server/.env")

from blofin_client import BloFinClient

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')

print(f"Placing $1 market order on BloFin: {base_url}")
print(f"API Key: {api_key[:10]}...")

# Initialize client
client = BloFinClient(
    api_key=api_key,
    secret_key=secret_key,
    passphrase=passphrase,
    base_url=base_url
)

symbol = "BTC-USDT"
side = "buy"

# For $1 notional, get current price and calculate contract size
try:
    # Place minimum allowed order size (0.1 contracts)
    size = 0.1
    # Minimal payload: only required fields
    payload = {
        "instId": symbol,
        "marginMode": "cross",
        "positionSide": "net",  # Required: net for One-way Mode, long/short for Hedge Mode
        "side": side,
        "orderType": "market",
        "size": str(size)
    }
    print(f"Placing minimal market order: {payload}")
    # Use the internal _request method directly for full control
    result = client._request("POST", "/api/v1/trade/order", payload)
    print("\n=== Order Result ===")
    print(result)
except Exception as e:
    print(f"\n❌ Error placing trade: {e}")
