#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("ACCOUNT STATUS:")
print("=" * 40)

bal = client.get_account_balance()
print(f"Total Equity: ${float(bal.get('totalEquity', 0)):.2f}")
print(f"Available: ${float(bal.get('availableBalance') or 0):.2f}")
print(f"Margin Used: ${float(bal.get('totalEquity', 0)) - float(bal.get('availableBalance') or 0):.2f}")

print("\nPOSITIONS:")
print("=" * 40)
positions = client._request("GET", "/api/v1/copytrading/account/positions-by-contract")
if positions and len(positions) > 0:
    for p in positions:
        print(f"{p.get('instId')}: {p.get('positions')} contracts")
else:
    print("No open positions")
