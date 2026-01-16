#!/usr/bin/env python3
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

print("=" * 60)
print("COPYTRADING ACCOUNT STATUS")
print("=" * 60)

# Get positions using copytrading endpoint
positions = client.get_positions()

if positions and len(positions) > 0:
    print(f"\n✅ Found {len(positions)} open positions:\n")
    for pos in positions:
        inst_id = pos.get('instId')
        contracts = pos.get('positions')
        side = pos.get('positionSide', 'net')
        entry = pos.get('averagePrice')
        mark = pos.get('markPrice')
        pnl = pos.get('unrealizedPnl')
        pnl_pct = float(pos.get('unrealizedPnlRatio', 0)) * 100
        
        print(f"{inst_id} - {side.upper()}: {contracts} contracts")
        print(f"  Entry: ${float(entry):.6f} | Mark: ${float(mark):.6f}")
        print(f"  Unrealized PnL: ${float(pnl):+.2f} ({pnl_pct:+.2f}%)")
        print()
else:
    print("\n❌ No open positions")

# Get balance
bal = client.get_account_balance()
available = float(bal.get('details', [{}])[0].get('available', 0))
equity = float(bal.get('totalEquity', 0))

print("=" * 60)
print(f"Total Equity: ${equity:.2f}")
print(f"Available: ${available:.2f}")
print(f"Margin Used: ${equity - available:.2f}")
print("=" * 60)
