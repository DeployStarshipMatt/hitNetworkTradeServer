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
base_url = os.getenv('BLOFIN_BASE_URL', 'https://demo-trading-openapi.blofin.com')

print(f"Testing BloFin connection to: {base_url}")
print(f"API Key: {api_key[:10]}...")

# Initialize client
client = BloFinClient(
    api_key=api_key,
    secret_key=secret_key,
    passphrase=passphrase,
    base_url=base_url
)

# Get account balance
try:
    balance = client.get_account_balance()
    print("\n=== Account Balance ===")
    print(balance)
    
    if balance and 'data' in balance:
        print("\n=== Formatted Balance ===")
        for item in balance['data']:
            ccy = item.get('ccy', 'Unknown')
            avail = item.get('availBal', '0')
            equity = item.get('eq', '0')
            print(f"{ccy}: Available=${avail}, Equity=${equity}")
except Exception as e:
    print(f"\n❌ Error: {e}")
