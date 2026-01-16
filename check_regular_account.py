#!/usr/bin/env python3
"""Check REGULAR account balance (not copytrading)"""
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

print("Fetching REGULAR account balance...")
# Use regular trading endpoint
response = client._request("GET", "/api/v1/account/balance")

if response:
    if isinstance(response, list) and len(response) > 0:
        details = response[0]
    elif isinstance(response, dict):
        details = response
    else:
        details = {}
    
    print(f"\n💰 Regular Trading Account Balance:")
    print(f"  Total Equity: ${float(details.get('equity', 0)):.2f}")
    print(f"  Available: ${float(details.get('available', 0)):.2f}")
    print(f"  Frozen: ${float(details.get('frozen', 0)):.2f}")
    print(f"  Unrealized PnL: ${float(details.get('unrealizedPnl', 0)):.2f}")
else:
    print("Failed to fetch balance")

print("\nFetching REGULAR account positions...")
positions = client._request("GET", "/api/v1/account/positions")
if positions:
    print(f"\nOpen Positions ({len(positions)}):")
    for pos in positions:
        if float(pos.get('availPos', 0)) != 0:
            print(f"  {pos.get('instId')}: {pos.get('availPos')} contracts")
            print(f"    Unrealized PnL: ${float(pos.get('unrealizedPnl', 0)):.2f}")
            print(f"    Avg Price: ${float(pos.get('avgPrice', 0)):.2f}")
