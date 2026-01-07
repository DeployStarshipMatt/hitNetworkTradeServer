import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# Get all positions
positions = client.get_positions()

print("All Open Positions:")
print("=" * 60)
for p in positions:
    print(f"\n{p['instId']}:")
    print(f"  Size: {p['positions']}")
    print(f"  Entry: ${p['averagePrice']}")
    print(f"  Current: ${p['markPrice']}")
    print(f"  PnL: ${p['unrealizedPnl']}")
    print(f"  Leverage: {p['leverage']}x")
    print(f"  Created: {p['createTime']}")
