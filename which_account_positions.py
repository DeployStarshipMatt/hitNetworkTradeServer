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

print("=" * 60)
print("CHECKING WHICH ACCOUNT HAS THE POSITIONS")
print("=" * 60)

print("\n1. REGULAR TRADING ACCOUNT (/api/v1/trade/positions):")
print("-" * 60)
try:
    regular_pos = client._request("GET", "/api/v1/trade/positions")
    if regular_pos and isinstance(regular_pos, list) and len(regular_pos) > 0:
        print(f"Found {len(regular_pos)} positions:")
        for pos in regular_pos:
            print(f"  - {pos.get('instId')}: {pos.get('positions')} contracts")
    else:
        print("No positions")
except Exception as e:
    print(f"Error: {e}")

print("\n2. COPYTRADING ACCOUNT (/api/v1/copytrading/trade/positions):")
print("-" * 60)
try:
    copy_pos = client._request("GET", "/api/v1/copytrading/trade/positions")
    if copy_pos and isinstance(copy_pos, list) and len(copy_pos) > 0:
        print(f"Found {len(copy_pos)} positions:")
        for pos in copy_pos:
            print(f"  - {pos.get('instId')}: {pos.get('positions')} contracts")
    else:
        print("No positions")
except Exception as e:
    print(f"Error: {e}")

print("\n3. GENERAL ACCOUNT (/api/v1/account/positions):")
print("-" * 60)
try:
    account_pos = client._request("GET", "/api/v1/account/positions")
    if account_pos and isinstance(account_pos, list) and len(account_pos) > 0:
        print(f"Found {len(account_pos)} positions:")
        for pos in account_pos:
            print(f"  - {pos.get('instId')}: {pos.get('positions')} contracts")
    else:
        print("No positions")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("ANSWER: The positions are on whichever endpoint returns data above")
print("=" * 60)
