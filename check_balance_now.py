#!/usr/bin/env python3
"""Check account balance"""
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

print("Fetching account balance...")
balance = client.get_account_balance()

if balance and 'details' in balance:
    details = balance['details'][0]
    print(f"\n💰 Copy Trading Account Balance:")
    print(f"  Total Equity: ${float(details.get('equity', 0)):.2f}")
    print(f"  Available: ${float(details.get('available', 0)):.2f}")
    print(f"  Frozen: ${float(details.get('frozen', 0)):.2f}")
    print(f"  Unrealized PnL: ${float(details.get('unrealizedPnl', 0)):.2f}")
else:
    print("Failed to fetch balance")
