#!/usr/bin/env python3
"""
Set 3 TP levels for CAKE and XLM positions
Each TP gets 1/3 of position with same SL
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
    
    print("📊 Fetching positions...\n")
    positions = client.get_positions()
    
    for pos in positions:
        symbol = pos.get('instId')
        size = float(pos.get('positions', 0))
        entry = float(pos.get('averagePrice', 0))
        margin_mode = pos.get('marginMode', 'cross')
        
        if size == 0:
            continue
        
        is_long = size > 0
        abs_size = abs(size)
        
        print(f"{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Position: {abs_size} contracts ({'LONG' if is_long else 'SHORT'})")
        print(f"Entry: ${entry}")
        
        # Cancel existing TP/SL orders
        print(f"\n🗑️  Canceling existing TP/SL orders...")
        try:
            response = client._request("GET", f"/api/v1/copytrading/trade/pending-tpsl-by-contract?instId={symbol}")
            
            if isinstance(response, list):
                for order in response:
                    algo_id = order.get('algoId')
                    try:
                        client._request("POST", "/api/v1/copytrading/trade/cancel-tpsl-by-contract", {
                            "algoId": algo_id
                        })
                        print(f"   ✅ Canceled order {algo_id}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to cancel {algo_id}: {e}")
        except Exception as e:
            print(f"   ⚠️  Error checking existing orders: {e}")
        
        # Calculate TP levels and SL
        if is_long:
            tp1_price = round(entry * 1.05, 6)  # 5% profit
            tp2_price = round(entry * 1.10, 6)  # 10% profit
            tp3_price = round(entry * 1.15, 6)  # 15% profit
            sl_price = round(entry * 0.95, 6)   # 5% stop loss
        else:
            tp1_price = round(entry * 0.95, 6)
            tp2_price = round(entry * 0.90, 6)
            tp3_price = round(entry * 0.85, 6)
            sl_price = round(entry * 1.05, 6)
        
        # Split position into 3 parts
        size_per_tp = abs_size / 3
        size_tp1 = round(size_per_tp, 1)
        size_tp2 = round(size_per_tp, 1)
        size_tp3 = abs_size - size_tp1 - size_tp2  # Remainder goes to TP3
        
        print(f"\n💡 Creating 3 TP levels:")
        print(f"   TP1: {size_tp1} contracts @ ${tp1_price} (+5%)")
        print(f"   TP2: {size_tp2} contracts @ ${tp2_price} (+10%)")
        print(f"   TP3: {size_tp3} contracts @ ${tp3_price} (+15%)")
        print(f"   SL:  All @ ${sl_price} (-5%)")
        
        # Create 3 TP/SL pairs
        tp_levels = [
            (size_tp1, tp1_price, "TP1 (+5%)"),
            (size_tp2, tp2_price, "TP2 (+10%)"),
            (size_tp3, tp3_price, "TP3 (+15%)")
        ]
        
        for size, tp_price, label in tp_levels:
            try:
                result = client.set_tpsl_pair(
                    symbol=symbol,
                    tp_price=tp_price,
                    sl_price=sl_price,
                    size=size,
                    trade_mode=margin_mode
                )
                print(f"   ✅ {label}: {size} contracts")
            except Exception as e:
                print(f"   ❌ Failed {label}: {e}")
        
        print()
    
    print(f"{'='*60}")
    print("✅ Done! All positions now have 3 TP levels")

if __name__ == "__main__":
    main()
