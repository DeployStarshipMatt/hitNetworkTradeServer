"""
Quick script to check for open positions on BloFin trading account.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os
from datetime import datetime

# Load trading server env
load_dotenv("trading-server/.env")

from blofin_client import BloFinClient

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://demo-trading-openapi.blofin.com')

print(f"Checking positions on: {base_url}")
print(f"API Key: {api_key[:10] if api_key else 'NOT SET'}...\n")

# Initialize client
client = BloFinClient(
    api_key=api_key,
    secret_key=secret_key,
    passphrase=passphrase,
    base_url=base_url
)

# Get open positions
try:
    positions = client.get_positions()
    
    if not positions or len(positions) == 0:
        print("✅ No open positions found.")
    else:
        print(f"📊 Found {len(positions)} open position(s):\n")
        print("=" * 80)
        
        for i, pos in enumerate(positions, 1):
            # Convert timestamps
            create_time = int(pos.get('createTime', 0)) / 1000
            update_time = int(pos.get('updateTime', 0)) / 1000
            create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
            update_dt = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\nPosition #{i}:")
            print(f"  Symbol: {pos.get('instId', 'N/A')}")
            print(f"  Position Side: {pos.get('positionSide', 'N/A')}")
            print(f"  Size: {pos.get('positions', 'N/A')} contracts")
            print(f"  Available: {pos.get('availablePositions', 'N/A')} contracts")
            print(f"  Entry Price: ${pos.get('averagePrice', 'N/A')}")
            print(f"  Mark Price: ${pos.get('markPrice', 'N/A')}")
            print(f"  Unrealized P&L: ${pos.get('unrealizedPnl', 'N/A')}")
            print(f"  Unrealized P&L Ratio: {float(pos.get('unrealizedPnlRatio', 0)) * 100:.2f}%")
            print(f"  Leverage: {pos.get('leverage', 'N/A')}x")
            print(f"  Margin Mode: {pos.get('marginMode', 'N/A')}")
            print(f"  ADL Level: {pos.get('adl', 'N/A')}/5")
            print(f"  Opened: {create_dt}")
            print(f"  Last Updated: {update_dt}")
            print("-" * 80)
            
except Exception as e:
    print(f"❌ Error checking positions: {e}")
    import traceback
    traceback.print_exc()
