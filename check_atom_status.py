import sys; sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()
c = BloFinClient(os.getenv('BLOFIN_API_KEY'), os.getenv('BLOFIN_SECRET_KEY'), os.getenv('BLOFIN_PASSPHRASE'))
pos = [p for p in c.get_positions() if p['instId'] == 'ATOM-USDT']

if pos:
    p = pos[0]
    print(f"ATOM Position:")
    print(f"  Size: {p['positions']}")
    print(f"  Entry: ${p['averagePrice']}")
    print(f"  Current Price: ${p['markPrice']}")
    print(f"  Unrealized PnL: ${p['unrealizedPnl']}")
    print(f"  Leverage: {p['leverage']}x")
    print(f"  Margin: ${p['initialMargin']}")
else:
    print("No ATOM position found - may have been closed")
