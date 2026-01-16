#!/usr/bin/env python3
"""
Quick script: Setup TP1 for cascading 3-level TPs on current positions.
Uses fractional size -0.33 (33% of position).
"""

import sys
sys.path.insert(0, '/opt/hitNetworkAutomation/trading-server')

from blofin_client import BloFinClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/opt/hitNetworkAutomation/trading-server/.env')

def main():
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE')
    )
    
    print("📊 Fetching positions...")
    positions = client.get_positions()
    
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
        
        # First, cancel existing TP/SL
        print("\n🗑️  Canceling existing TP/SL...")
        try:
            # Get pending orders via raw API call
            pending = client._request("GET", "/api/v1/copytrading/trade/pending-tpsl-by-contract")
            for order in pending:
                if order['instId'] == symbol:
                    algo_id = order['algoId']
                    client._request("POST", "/api/v1/copytrading/trade/cancel-tpsl-by-contract", {"algoId": algo_id})
                    print(f"   ✅ Canceled order {algo_id}")
        except Exception as e:
            print(f"   ⚠️  Cancel failed (might be none): {e}")
        
        # Calculate prices
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
        
        print(f"\n🎯 Creating TP1 (33% of position)...")
        
        # Calculate actual contract amounts for 3 TP levels
        abs_size = abs(size)
        size_tp1 = round(abs_size / 3, 1)  # 33%
        size_tp2 = round(abs_size / 3, 1)  # 33%
        size_tp3 = abs_size - size_tp1 - size_tp2  # Remainder (34%)
        
        print(f"   TP1: {size_tp1} contracts @ ${tp1_price} (+5%)")
        print(f"   TP2: {size_tp2} contracts @ ${tp2_price} (+10%) [will auto-create]")
        print(f"   TP3: {size_tp3} contracts @ ${tp3_price} (+15%) [will auto-create]")
        print(f"   SL:  @ ${sl_price} (-5%)")
        
        try:
            result = client.set_tpsl_pair(
                symbol=symbol,
                tp_price=tp1_price,
                sl_price=sl_price,
                size=size_tp1,  # Actual contract amount
                trade_mode="cross"
            )
            print(f"   ✅ TP1 created successfully")
            print(f"   📝 TP2 (+10%) and TP3 (+15%) will auto-create when TP1 fills")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Done! TP1 set for all positions")
    print("📌 TP2/TP3 will be created automatically by order_monitor when TP1 fills")

if __name__ == "__main__":
    main()
