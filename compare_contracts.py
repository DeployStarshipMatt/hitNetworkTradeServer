"""
Compare contract specifications for BTC and ATOM
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

print("Contract Specifications Comparison:\n")

for inst in response:
    symbol = inst.get('instId')
    if symbol in ['BTC-USDT', 'ATOM-USDT']:
        print(f"{symbol}:")
        print(f"  Min Size: {inst.get('minSize')}")
        print(f"  Lot Size: {inst.get('lotSize')} (smallest increment you can trade)")
        print(f"  Contract Value: {inst.get('ctVal')}")
        print(f"  Contract Type: {inst.get('contractType')}")
        
        lot_size = float(inst.get('lotSize', 1))
        if lot_size < 1:
            print(f"  ✅ Partial contracts allowed (can trade {lot_size}, {lot_size*2}, {lot_size*3}, etc.)")
        else:
            print(f"  ❌ Only whole contracts (must trade 1, 2, 3, etc.)")
        print()
