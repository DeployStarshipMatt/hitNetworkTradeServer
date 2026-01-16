#!/usr/bin/env python3
"""
Replace existing TP/SL orders with better ones (proper TP targets)
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
    
    print("📊 Fetching positions and current TP/SL orders...\n")
    positions = client.get_positions()
    
    for pos in positions:
        symbol = pos.get('instId')
        size = float(pos.get('positions', 0))
        entry = float(pos.get('averagePrice', 0))
        mark = float(pos.get('markPrice', 0))
        margin_mode = pos.get('marginMode', 'cross')
        
        if size == 0:
            continue
        
        is_long = size > 0
        abs_size = abs(size)
        
        print(f"{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Position: {size} contracts ({'LONG' if is_long else 'SHORT'})")
        print(f"Entry: ${entry}")
        print(f"Current: ${mark}")
        
        # Get existing TP/SL orders
        try:
            response = client._request("GET", f"/api/v1/copytrading/trade/pending-tpsl-by-contract?instId={symbol}")
            
            if isinstance(response, list) and len(response) > 0:
                print(f"\n📋 Found {len(response)} existing TP/SL order(s):")
                for order in response:
                    algo_id = order.get('algoId')
                    tp = float(order.get('tpTriggerPrice', 0))
                    sl = float(order.get('slTriggerPrice', 0))
                    
                    print(f"   Order {algo_id}: TP=${tp}, SL=${sl}")
                    
                    # Cancel this order
                    print(f"   🗑️  Canceling order {algo_id}...")
                    try:
                        cancel_response = client._request("POST", "/api/v1/copytrading/trade/cancel-tpsl-by-contract", {
                            "algoId": algo_id
                        })
                        print(f"   ✅ Canceled")
                    except Exception as e:
                        print(f"   ❌ Cancel failed: {e}")
                        continue
            else:
                print(f"\n📋 No existing TP/SL orders")
        
        except Exception as e:
            print(f"\n⚠️  Error checking existing orders: {e}")
        
        # Calculate new TP and SL levels
        if is_long:
            tp_price = round(entry * 1.10, 6)  # 10% profit target
            sl_price = round(entry * 0.95, 6)  # 5% stop loss
        else:
            tp_price = round(entry * 0.90, 6)
            sl_price = round(entry * 1.05, 6)
        
        print(f"\n💡 Proposed new TP/SL:")
        print(f"   TP: ${tp_price} ({'+10%' if is_long else '-10%'})")
        print(f"   SL: ${sl_price} ({'-5%' if is_long else '+5%'})")
        print(f"   Size: {abs_size} contracts")
        
        response = input(f"\n⚠️  Set new TP/SL for {symbol}? (y/n): ")
        if response.lower() != 'y':
            print("⏭️  Skipped\n")
            continue
        
        # Create new TP/SL order
        try:
            result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp_price,
                sl_price=sl_price,
                size=abs_size,
                trade_mode=margin_mode
            )
            
            print(f"✅ New TP/SL order created!")
            print(f"   Algo ID: {result.get('order_id')}\n")
            
        except Exception as e:
            print(f"❌ Failed to create new TP/SL: {e}\n")
    
    print(f"{'='*60}")
    print("✅ Done!")

if __name__ == "__main__":
    main()
