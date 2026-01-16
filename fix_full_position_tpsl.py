#!/usr/bin/env python3
"""
Fix TP/SL to cover FULL position (not just 1/3)
BloFin API only allows 1 TP/SL order per position.
"""

import sys
import os
sys.path.insert(0, '/opt/hitNetworkAutomation')

from trading_server.blofin_client import BlofinClient

def main():
    client = BlofinClient()
    
    print("📊 Fetching positions...")
    positions = client.get_copytrading_positions()
    
    if not positions:
        print("❌ No open positions found")
        return
    
    for pos in positions:
        symbol = pos['instId']
        size = float(pos['positions'])
        entry = float(pos['averagePrice'])
        side = pos['positionSide']
        
        print(f"\n{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Position: {size} contracts ({'LONG' if size > 0 else 'SHORT'})")
        print(f"Entry: ${entry}")
        
        # Check if there's an existing TP/SL order
        print("\n🗑️  Checking for existing TP/SL orders...")
        pending_orders = client.get_pending_tpsl()
        existing_order = None
        for order in pending_orders:
            if order['instId'] == symbol:
                existing_order = order
                break
        
        if existing_order:
            algo_id = existing_order['algoId']
            print(f"   Found order {algo_id}, canceling...")
            try:
                client.cancel_tpsl(algo_id)
                print(f"   ✅ Canceled order {algo_id}")
            except Exception as e:
                print(f"   ❌ Failed to cancel: {e}")
                continue
        
        # Calculate TP/SL for full position
        abs_size = abs(size)
        
        if size > 0:  # LONG
            tp_price = round(entry * 1.10, 6)  # +10% profit
            sl_price = round(entry * 0.95, 6)  # -5% loss
        else:  # SHORT
            tp_price = round(entry * 0.90, 6)  # +10% profit
            sl_price = round(entry * 1.05, 6)  # -5% loss
        
        print(f"\n💡 Setting TP/SL for FULL position:")
        print(f"   Size: {abs_size} contracts")
        print(f"   TP: ${tp_price} (+10%)")
        print(f"   SL: ${sl_price} (-5%)")
        
        try:
            result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp_price,
                sl_price=sl_price,
                size=abs_size,
                trade_mode="cross"
            )
            print(f"   ✅ TP/SL set successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Done! All positions protected with full-size TP/SL")

if __name__ == "__main__":
    main()
