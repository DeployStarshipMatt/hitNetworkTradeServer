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

# We need about 193 SEI total for 1% risk
# Currently have 1 SEI, need 192 more
# Try placing in batches of 50

target_total = 193
current_size = 1  # Current position
needed = target_total - current_size

print(f"Target: {target_total} SEI")
print(f"Current: {current_size} SEI")
print(f"Need to add: {needed} SEI")
print()

# Try batches of 50
batch_size = 50
batches = needed // batch_size
remainder = needed % batch_size

print(f"Will place {batches} batches of {batch_size} SEI")
if remainder > 0:
    print(f"Plus 1 batch of {remainder} SEI")
print()

# Place orders
for i in range(batches):
    print(f"Batch {i+1}: Placing {batch_size} SEI...")
    try:
        result = client.place_market_order("SEI-USDT", "sell", batch_size)
        print(f"  Success: {result.get('status')}")
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  Stopping here due to error")
        break

if remainder > 0 and batches > 0:
    print(f"\nFinal batch: Placing {remainder} SEI...")
    try:
        result = client.place_market_order("SEI-USDT", "sell", remainder)
        print(f"  Success: {result.get('status')}")
    except Exception as e:
        print(f"  FAILED: {e}")

print("\nChecking final position size...")
pos = [p for p in client.get_positions() if p['instId'] == 'SEI-USDT'][0]
print(f"Final SEI position: {pos['positions']} @ ${pos['averagePrice']}")
