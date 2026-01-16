#!/usr/bin/env python3
"""
Migrate existing CAKE and XLM positions to new 3-TP system
1. Cancel old TP/SL orders
2. Place 3 reduce-only limit orders for TPs
3. Place new SL order
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trading-server'))
from blofin_client import BloFinClient

load_dotenv()

def main():
    client = BloFinClient(
        api_key=os.getenv("BLOFIN_API_KEY"),
        secret_key=os.getenv("BLOFIN_SECRET_KEY"),
        passphrase=os.getenv("BLOFIN_PASSPHRASE")
    )
    
    # Get current positions
    positions = client.get_positions()
    print(f"📊 Found {len(positions)} positions\n")
    
    for pos in positions:
        symbol = pos.get("instId", "")
        size = float(pos.get("positions", 0))
        avg_price = float(pos.get("averagePrice", 0))
        
        if size == 0:
            continue
        
        print(f"{'='*60}")
        print(f"📍 Migrating: {symbol}")
        print(f"   Size: {size} contracts @ ${avg_price:.4f}")
        
        # Step 1: Cancel existing TP/SL orders
        print(f"\n🗑️  Canceling old TP/SL orders...")
        try:
            cancel_result = client.cancel_tpsl(symbol=symbol, size="-1")
            print(f"   ✅ Canceled old TP/SL orders")
        except Exception as e:
            print(f"   ⚠️  Cancel failed (might not exist): {e}")
        
        # Calculate TP levels (+5%, +10%, +15% from entry)
        tp1_price = avg_price * 1.05
        tp2_price = avg_price * 1.10
        tp3_price = avg_price * 1.15
        sl_price = avg_price * 0.95  # -5% SL
        
        # Split position into thirds
        tp_size = size / 3
        tp_sizes = [
            round(tp_size, 1),
            round(tp_size, 1),
            size - 2 * round(tp_size, 1)  # Remainder
        ]
        
        print(f"\n🎯 Placing 3 TP levels:")
        print(f"   TP1: ${tp1_price:.4f} ({tp_sizes[0]} contracts)")
        print(f"   TP2: ${tp2_price:.4f} ({tp_sizes[1]} contracts)")
        print(f"   TP3: ${tp3_price:.4f} ({tp_sizes[2]} contracts)")
        print(f"   SL:  ${sl_price:.4f} (full position)")
        
        # Place 3 reduce-only limit orders
        tp_prices = [tp1_price, tp2_price, tp3_price]
        for i, (tp_price, tp_size) in enumerate(zip(tp_prices, tp_sizes), 1):
            try:
                tp_result = client.place_reduce_only_limit_order(
                    symbol=symbol,
                    side="sell",  # Long positions close with sell
                    size=tp_size,
                    price=tp_price,
                    trade_mode="cross",
                    position_side="net"
                )
                order_id = tp_result.get("order_id")
                print(f"   ✅ TP{i} order placed: {order_id}")
            except Exception as e:
                print(f"   ❌ TP{i} failed: {e}")
        
        # Place SL order using TP/SL endpoint (with placeholder TP)
        print(f"\n🛑 Placing stop-loss...")
        try:
            sl_result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp3_price,  # Placeholder (won't trigger, TP3 limit order is higher)
                sl_price=sl_price,
                size="-1",  # Full position
                trade_mode="cross"
            )
            print(f"   ✅ SL order placed @ ${sl_price:.4f}")
        except Exception as e:
            print(f"   ❌ SL failed: {e}")
        
        print()
    
    print(f"{'='*60}")
    print("✅ Migration complete!")

if __name__ == "__main__":
    main()
