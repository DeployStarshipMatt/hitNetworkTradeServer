#!/usr/bin/env python3
"""Check all pending limit orders"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trading-server'))
from blofin_client import BloFinClient

load_dotenv()

client = BloFinClient(
    api_key=os.getenv("BLOFIN_API_KEY"),
    secret_key=os.getenv("BLOFIN_SECRET_KEY"),
    passphrase=os.getenv("BLOFIN_PASSPHRASE")
)

# Get pending orders
pending = client.get_pending_orders()
print(f"📊 Found {len(pending)} pending orders\n")

for order in pending:
    print(f"Order ID: {order.get('orderId')}")
    print(f"   Symbol: {order.get('instId')}")
    print(f"   Type: {order.get('orderType')}")
    print(f"   Side: {order.get('side')}")
    print(f"   Size: {order.get('size')}")
    print(f"   Price: {order.get('price')}")
    print(f"   Status: {order.get('status')}")
    print()
