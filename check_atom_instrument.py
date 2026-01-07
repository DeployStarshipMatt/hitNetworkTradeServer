"""
Check ATOM-USDT instrument specifications
"""
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

# Get instrument info
response = client._request("GET", "/api/v1/market/instruments", {"instType": "SWAP"})

# Find ATOM-USDT
for inst in response:
    if inst.get('instId') == 'ATOM-USDT':
        print("ATOM-USDT Instrument Specifications:")
        print(f"  Contract Value (ctVal): {inst.get('ctVal')}")
        print(f"  Contract Type: {inst.get('contractType')}")
        print(f"  Minimum Size (minSize): {inst.get('minSize')}")
        print(f"  Lot Size (lotSize): {inst.get('lotSize')}")
        print(f"  Tick Size (tickSize): {inst.get('tickSize')}")
        print(f"\nWhat 1 contract means: {inst.get('ctVal')} ATOM")
        print(f"What 3 contracts means: {float(inst.get('ctVal')) * 3} ATOM")
        print(f"\nCan you use decimals? Lot size = {inst.get('lotSize')} (if 0.1, then yes)")
        break
