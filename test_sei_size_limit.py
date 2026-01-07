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

# Try progressively larger sizes to find the limit
test_sizes = [5, 10, 20, 50, 100]

for size in test_sizes:
    print(f"\nTrying {size} SEI...")
    try:
        result = client.place_market_order("SEI-USDT", "sell", size)
        print(f"  SUCCESS: {result}")
        
        # If successful, close it immediately
        print(f"  Closing position...")
        close_result = client.place_market_order("SEI-USDT", "buy", size)
        print(f"  Closed: {close_result}")
        break
        
    except Exception as e:
        print(f"  FAILED: {e}")
