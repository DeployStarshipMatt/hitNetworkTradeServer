"""
Print full raw position data
"""
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

# Get raw position data
positions = client._request("GET", "/api/v1/account/positions")

print("Full raw API response:")
print(json.dumps(positions, indent=2))
