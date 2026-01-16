#!/usr/bin/env python3
"""Check trade history"""
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

print("Fetching Copy Trading order history...")
try:
    # Get filled orders from today
    orders = client._request("GET", "/api/v1/copytrading/trade/orders-history", {
        "instType": "SWAP",
        "state": "filled"
    })
    
    if orders and len(orders) > 0:
        print(f"\n📋 Recent Filled Orders ({len(orders)}):\n")
        for order in orders[:10]:  # Show last 10
            symbol = order.get('instId', 'N/A')
            side = order.get('side', 'N/A')
            size = order.get('fillSize', order.get('size', '0'))
            price = order.get('fillPrice', order.get('avgPrice', '0'))
            timestamp = order.get('fillTime', order.get('updateTime', '0'))
            pnl = order.get('pnl', '0')
            
            # Convert timestamp to readable format
            if timestamp and timestamp != '0':
                try:
                    dt = datetime.fromtimestamp(int(timestamp)/1000)
                    time_str = dt.strftime('%m/%d %H:%M:%S')
                except:
                    time_str = str(timestamp)
            else:
                time_str = 'N/A'
            
            try:
                price_val = float(price) if price else 0.0
                pnl_val = float(pnl) if pnl else 0.0
                print(f"  {time_str} | {symbol:12} | {side:5} | Size: {size:8} | Price: ${price_val:>10.2f} | PnL: ${pnl_val:>7.2f}")
            except Exception as e:
                print(f"  {symbol} | {side} | Size: {size} | Error parsing: {e}")
    else:
        print("No recent filled orders")
        
except Exception as e:
    print(f"Error fetching orders: {e}")

print("\n" + "="*80)
print("Checking pending orders...")
try:
    pending = client._request("GET", "/api/v1/copytrading/trade/orders-pending")
    if pending and len(pending) > 0:
        print(f"\n⏳ Pending Orders ({len(pending)}):")
        for order in pending:
            print(f"  {order.get('instId')}: {order.get('side')} {order.get('size')} @ {order.get('price', 'market')}")
    else:
        print("No pending orders")
except Exception as e:
    print(f"Error fetching pending orders: {e}")
