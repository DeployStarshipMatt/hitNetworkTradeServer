#!/usr/bin/env python3
"""Emergency: Set stop loss on BTC position"""
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

print("Setting emergency stop loss on BTC position...")
# Entry was $95,501.75, set SL at -2% = $93,591.71
sl_price = 93591.71
size = 5.2

try:
    result = client.set_stop_loss(
        symbol='BTC-USDT',
        side='sell',  # Sell to close long
        size=size,
        trigger_price=sl_price,
        trade_mode='cross'
    )
    print(f"✅ Stop loss set at ${sl_price}: {result}")
except Exception as e:
    print(f"❌ Failed: {e}")
