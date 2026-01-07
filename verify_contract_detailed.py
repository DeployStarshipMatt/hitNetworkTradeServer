"""
Get detailed position info to verify contract size
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

# Get raw position data
positions = client._request("GET", "/api/v1/account/positions")

for pos in positions:
    if pos.get('instId') == 'ATOM-USDT':
        print("Raw ATOM-USDT Position Data:")
        print(f"  positionSize: {pos.get('positionSize')}")
        print(f"  availablePosition: {pos.get('availablePosition')}")
        print(f"  averagePrice: {pos.get('averagePrice')}")
        print(f"  notionalValue: {pos.get('notionalValue')}")
        print(f"  unrealizedPnl: {pos.get('unrealizedPnl')}")
        
        size = abs(float(pos.get('positionSize', 0)))
        entry = float(pos.get('averagePrice', 0))
        notional = abs(float(pos.get('notionalValue', 0)))
        
        print(f"\nCalculations:")
        print(f"  Position size: {size} contracts")
        print(f"  Entry price: ${entry}")
        print(f"  Actual notional value: ${notional}")
        
        print(f"\nScenario 1: If 1 contract = 1 ATOM token")
        print(f"  {size} ATOM × ${entry} = ${size * entry}")
        
        print(f"\nScenario 2: If 1 contract = $1 USD")
        print(f"  {size} contracts = ${size}")
        
        print(f"\n{'='*50}")
        if abs(notional - size) < 0.1:
            print(f"✅ CONFIRMED: 1 contract = $1 USD")
            print(f"Your position is ${size} worth of ATOM, NOT {size} ATOM tokens")
        elif abs(notional - (size * entry)) < 0.1:
            print(f"✅ CONFIRMED: 1 contract = 1 ATOM token")
            print(f"Your position is {size} ATOM tokens worth ${size * entry}")
