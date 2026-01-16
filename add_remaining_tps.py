#!/usr/bin/env python3
"""
Add TP2 and TP3 to existing CAKE and XLM positions
Currently they only have TP1, need to add the remaining 2 TPs
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
    print(f"📊 Found {len(positions)} positions")
    
    for pos in positions:
        symbol = pos.get("instId", "")
        size = float(pos.get("positions", 0))
        avg_price = float(pos.get("averagePrice", 0))
        unrealized_pnl = float(pos.get("unrealizedProfit", 0))
        
        if size == 0:
            continue
        
        print(f"\n{'='*60}")
        print(f"📍 Position: {symbol}")
        print(f"   Size: {size} contracts")
        print(f"   Entry: ${avg_price:.4f}")
        print(f"   P&L: ${unrealized_pnl:.2f}")
        
        # Calculate TP prices (same as server.py logic)
        # TP1 @ +5%, TP2 @ +10%, TP3 @ +15%
        tp1_price = avg_price * 1.05
        tp2_price = avg_price * 1.10
        tp3_price = avg_price * 1.15
        
        # Split position into thirds
        tp1_size = size / 3
        tp2_size = size / 3
        tp3_size = size - tp1_size - tp2_size  # Remainder
        
        print(f"   TP1: ${tp1_price:.4f} ({tp1_size:.1f} contracts) - Already set ✅")
        print(f"   TP2: ${tp2_price:.4f} ({tp2_size:.1f} contracts)")
        print(f"   TP3: ${tp3_price:.4f} ({tp3_size:.1f} contracts)")
        
        # Place TP2 reduce-only limit order
        print(f"\n🎯 Placing TP2 reduce-only limit order...")
        try:
            tp2_result = client.place_reduce_only_limit_order(
                symbol=symbol,
                side="sell",  # Long positions close with sell
                size=tp2_size,
                price=tp2_price,
                trade_mode="cross",
                position_side="net"
            )
            
            if tp2_result.get("success"):
                tp2_order = tp2_result["data"][0]
                print(f"   ✅ TP2 order placed: {tp2_order.get('orderId')}")
                print(f"      Price: ${tp2_price:.4f}, Size: {tp2_size:.1f} contracts")
            else:
                print(f"   ❌ TP2 failed: {tp2_result.get('error')}")
        except Exception as e:
            print(f"   ❌ TP2 failed: {e}")
        
        # Place TP3 reduce-only limit order
        print(f"\n🎯 Placing TP3 reduce-only limit order...")
        try:
            tp3_result = client.place_reduce_only_limit_order(
                symbol=symbol,
                side="sell",
                size=tp3_size,
                price=tp3_price,
                trade_mode="cross",
                position_side="net"
            )
            
            if tp3_result.get("success"):
                tp3_order = tp3_result["data"][0]
                print(f"   ✅ TP3 order placed: {tp3_order.get('orderId')}")
                print(f"      Price: ${tp3_price:.4f}, Size: {tp3_size:.1f} contracts")
            else:
                print(f"   ❌ TP3 failed: {tp3_result.get('error')}")
        except Exception as e:
            print(f"   ❌ TP3 failed: {e}")
    
    print(f"\n{'='*60}")
    print("✅ All remaining TPs added!")

if __name__ == "__main__":
    main()
