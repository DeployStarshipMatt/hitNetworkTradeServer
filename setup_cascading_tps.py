#!/usr/bin/env python3
"""
Setup cascading 3-level TPs for current positions.

Uses fractional position sizes:
- TP1: -0.33 (33% of position) at +5%
- TP2: -0.5 (50% of remaining = 33% total) at +10%
- TP3: -1 (100% of remaining = 33% total) at +15%
All with same SL at -5%
"""

import sys
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
        
        print(f"\n{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Position: {size} contracts ({'LONG' if size > 0 else 'SHORT'})")
        print(f"Entry: ${entry}")
        
        # Cancel any existing TP/SL orders
        print("\n🗑️  Canceling existing TP/SL orders...")
        pending_orders = client.get_pending_tpsl()
        for order in pending_orders:
            if order['instId'] == symbol:
                algo_id = order['algoId']
                try:
                    client.cancel_tpsl(algo_id)
                    print(f"   ✅ Canceled order {algo_id}")
                except Exception as e:
                    print(f"   ❌ Failed to cancel {algo_id}: {e}")
        
        # Calculate TP/SL prices
        if size > 0:  # LONG
            tp1_price = round(entry * 1.05, 6)  # +5%
            tp2_price = round(entry * 1.10, 6)  # +10%
            tp3_price = round(entry * 1.15, 6)  # +15%
            sl_price = round(entry * 0.95, 6)   # -5%
        else:  # SHORT
            tp1_price = round(entry * 0.95, 6)  # +5%
            tp2_price = round(entry * 0.90, 6)  # +10%
            tp3_price = round(entry * 0.85, 6)  # +15%
            sl_price = round(entry * 1.05, 6)   # -5%
        
        print(f"\n💡 Setting up 3-level cascading TPs:")
        print(f"   TP1: -0.33 (33%) @ ${tp1_price} (+5%)")
        print(f"   TP2: -0.5 (50% of remaining) @ ${tp2_price} (+10%)")
        print(f"   TP3: -1 (100% of remaining) @ ${tp3_price} (+15%)")
        print(f"   SL:  ${sl_price} (-5%)")
        
        # Create TP1 immediately
        print(f"\n🎯 Creating TP1...")
        try:
            result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp1_price,
                sl_price=sl_price,
                size="-0.33",  # 33% of position
                trade_mode="cross"
            )
            print(f"   ✅ TP1 created successfully")
            
            # Note: TP2 and TP3 will be created automatically by order_monitor
            # when TP1 and TP2 fill respectively
            print(f"   📝 TP2 and TP3 will auto-create when previous levels fill")
            
        except Exception as e:
            print(f"   ❌ Failed to create TP1: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Done! Cascading TPs configured")
    print("📌 Note: TP2 creates when TP1 fills, TP3 creates when TP2 fills")

if __name__ == "__main__":
    main()
