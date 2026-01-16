#!/usr/bin/env python3
"""
Check active TP/SL orders for copytrading positions
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'trading-server'))

from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE')
    )
    
    print("📊 Fetching positions...")
    positions = client.get_positions()
    
    print(f"\n✅ Found {len(positions)} positions\n")
    
    for pos in positions:
        symbol = pos.get('instId')
        size = float(pos.get('positions', 0))
        entry = float(pos.get('averagePrice', 0))
        mark = float(pos.get('markPrice', 0))
        pnl = float(pos.get('unrealizedPnl', 0))
        
        print(f"\n{'='*60}")
        print(f"📈 {symbol}")
        print(f"   Position: {size} contracts")
        print(f"   Entry: ${entry}")
        print(f"   Mark: ${mark}")
        print(f"   PnL: ${pnl}")
        
        # Try to get TP/SL orders for this symbol
        print(f"\n🔍 Checking TP/SL orders...")
        try:
            response = client._request("GET", f"/api/v1/copytrading/trade/pending-tpsl-by-contract?instId={symbol}")
            
            if isinstance(response, list) and len(response) > 0:
                print(f"   ✅ Found {len(response)} TP/SL order(s):")
                for order in response:
                    algo_id = order.get('algoId')
                    tp = order.get('tpTriggerPrice')
                    sl = order.get('slTriggerPrice')
                    order_size = order.get('size')
                    state = order.get('state')
                    
                    print(f"\n   Order ID: {algo_id}")
                    print(f"   Status: {state}")
                    print(f"   Size: {order_size}")
                    if tp:
                        print(f"   TP: ${tp}")
                    if sl:
                        print(f"   SL: ${sl}")
            else:
                print(f"   ❌ No active TP/SL orders found")
                
        except Exception as e:
            print(f"   ❌ Error checking TP/SL: {e}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
