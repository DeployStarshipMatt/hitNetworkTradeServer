"""
Check actual leverage on current positions
"""
import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, 'trading-server')

from blofin_client import BloFinClient

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("Checking actual leverage on positions...\n")

positions = client.get_positions()

for pos in positions:
    symbol = pos.get('instId')
    leverage = pos.get('leverage')
    size = pos.get('availableSize')
    side = pos.get('positionSide')
    
    print(f"{symbol}:")
    print(f"  Leverage: {leverage}")
    print(f"  Size: {size}")
    print(f"  Side: {side}")
    print()
