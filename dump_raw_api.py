#!/usr/bin/env python3
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

print("=" * 60)
print("RAW API RESPONSE - POSITIONS")
print("=" * 60)

positions = client._request("GET", "/api/v1/copytrading/account/positions-by-contract")
print(json.dumps(positions, indent=2))

print("\n" + "=" * 60)
print("RAW API RESPONSE - BALANCE")
print("=" * 60)

balance = client._request("GET", "/api/v1/copytrading/account/balance")
print(json.dumps(balance, indent=2))
