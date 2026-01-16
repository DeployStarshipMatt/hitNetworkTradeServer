#!/usr/bin/env python3
"""Emergency close BTC position"""
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

print("Fetching positions...")
positions = client.get_positions()

for pos in positions:
    if pos.get('instId') == 'BTC-USDT':
        size = abs(float(pos.get('availPos', 0)))
        if size > 0:
            print(f"Closing BTC position: {size} contracts")
            # Sell to close long position
            result = client.place_market_order(
                symbol='BTC-USDT',
                side='sell',
                size=size,
                trade_mode='cross'
            )
            print(f"✅ Position closed: {result}")
            break
else:
    print("No BTC position found")
