"""Check TP/SL orders in detail"""
import sys
import os
sys.path.append('trading-server')

from blofin_client import BloFinClient
from dotenv import load_dotenv
import json

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("Checking TP/SL for DASH, CRO, DYDX...\n")

for symbol in ['DASH-USDT', 'CRO-USDT', 'DYDX-USDT']:
    print(f"\n{'='*60}")
    print(f"{symbol}:")
    print('='*60)
    
    try:
        tpsl_orders = client.get_pending_tpsl(symbol)
        
        if tpsl_orders:
            print(f"Found {len(tpsl_orders)} TP/SL order(s):\n")
            for order in tpsl_orders:
                print(json.dumps(order, indent=2))
        else:
            print("❌ NO TP/SL ORDERS FOUND!")
            
    except Exception as e:
        print(f"❌ Error checking {symbol}: {e}")
