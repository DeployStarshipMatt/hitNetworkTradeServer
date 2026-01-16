#!/usr/bin/env python3
"""
Add TP/SL protection to current CAKE and XLM positions
"""
import sys
from pathlib import Path

# Add trading-server directory to path
sys.path.append(str(Path(__file__).parent / 'trading-server'))

from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize client
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE')
    )
    
    print("📊 Fetching current positions...")
    positions = client.get_positions()
    
    if not positions:
        print("❌ No positions found")
        return
    
    print(f"\n✅ Found {len(positions)} positions\n")
    
    # Process each position
    for pos in positions:
        symbol = pos.get('instId')
        size = float(pos.get('positions', 0))
        entry_price = float(pos.get('averagePrice', 0))
        mark_price = float(pos.get('markPrice', 0))
        margin_mode = pos.get('marginMode', 'cross')
        
        print(f"\n{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Size: {size} contracts")
        print(f"Entry: ${entry_price}")
        print(f"Current: ${mark_price}")
        print(f"Margin: {margin_mode}")
        
        # Skip if no position
        if size == 0:
            print("⏭️  Skipping - no position")
            continue
        
        # Determine if long or short
        is_long = size > 0
        abs_size = abs(size)
        
        # Calculate TP and SL levels based on position direction
        if is_long:
            # Long position: TP above, SL below
            tp_price = round(entry_price * 1.10, 6)  # 10% profit
            sl_price = round(entry_price * 0.95, 6)  # 5% loss
        else:
            # Short position: TP below, SL above
            tp_price = round(entry_price * 0.90, 6)  # 10% profit
            sl_price = round(entry_price * 1.05, 6)  # 5% loss
        
        print(f"\n📍 Setting protection:")
        print(f"  TP: ${tp_price} ({'LONG' if is_long else 'SHORT'})")
        print(f"  SL: ${sl_price}")
        print(f"  Size: {abs_size} contracts")
        
        # Confirm with user
        response = input(f"\n⚠️  Add TP/SL to {symbol}? (y/n): ")
        if response.lower() != 'y':
            print("⏭️  Skipped")
            continue
        
        try:
            # Use the new set_tpsl_pair method
            result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp_price,
                sl_price=sl_price,
                size=abs_size,
                trade_mode=margin_mode
            )
            
            print(f"✅ TP/SL protection added!")
            print(f"   Algo ID: {result.get('order_id')}")
            
        except Exception as e:
            print(f"❌ Failed to add protection: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Done!")

if __name__ == "__main__":
    main()
