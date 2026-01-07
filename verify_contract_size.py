"""
Check current ATOM position value
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

# Get positions
positions = client.get_positions()

for pos in positions:
    symbol = pos.get('instId')
    if symbol == 'ATOM-USDT':
        size = float(pos.get('positionSize', 0))
        entry = float(pos.get('averagePrice', 0))
        notional = float(pos.get('notionalValue', 0))
        
        print(f"ATOM-USDT Position:")
        print(f"  Size: {size} contracts")
        print(f"  Entry price: ${entry}")
        print(f"  Notional value: ${notional}")
        print(f"\nIf 1 contract = 1 ATOM token:")
        print(f"  {size} contracts × ${entry} = ${size * entry}")
        print(f"\nIf 1 contract = $1:")
        print(f"  {size} contracts = ${size}")
        print(f"\nActual notional from BloFin: ${notional}")
        
        if abs(notional - (size * entry)) < 0.01:
            print(f"\n✅ Confirmed: 1 contract = 1 ATOM token (size × price = notional)")
        elif abs(notional - size) < 0.01:
            print(f"\n✅ Confirmed: 1 contract = $1 USD (size = notional)")
