#!/usr/bin/env python3
"""Add TP/SL to XLM position"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'trading-server'))
from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Add TP/SL to XLM
result = client.set_tpsl_pair(
    symbol="XLM-USDT",
    tp_price=0.242918,  # +10%
    sl_price=0.209793,  # -5%
    size=9.4,
    trade_mode="cross"
)

print(f"✅ XLM TP/SL protection added!")
print(f"   TP: $0.242918 (+10%)")
print(f"   SL: $0.209793 (-5%)")
print(f"   Algo ID: {result.get('order_id')}")
