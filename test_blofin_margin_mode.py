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

print(f"Testing GET /api/v1/account/margin-mode on BloFin: {base_url}")
print(f"API Key: {api_key[:10]}...")

# Initialize client
client = BloFinClient(
    api_key=api_key,
    secret_key=secret_key,
    passphrase=passphrase,
    base_url=base_url
)

# Get margin mode
try:
    margin_mode = client._request("GET", "/api/v1/account/margin-mode")
    print("\n=== Margin Mode ===")
    print(margin_mode)
except Exception as e:
    print(f"\n❌ Error: {e}")
