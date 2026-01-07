"""
Script to close open position on BloFin trading account.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from dotenv import load_dotenv
import os
from datetime import datetime

# Load trading server env
load_dotenv("trading-server/.env")

from blofin_client import BloFinClient

# Get credentials
api_key = os.getenv('BLOFIN_API_KEY')
secret_key = os.getenv('BLOFIN_SECRET_KEY')
passphrase = os.getenv('BLOFIN_PASSPHRASE')
base_url = os.getenv('BLOFIN_BASE_URL', 'https://demo-trading-openapi.blofin.com')

print(f"Closing positions on: {base_url}")
print(f"API Key: {api_key[:10] if api_key else 'NOT SET'}...\n")

# Initialize client
client = BloFinClient(
    api_key=api_key,
    secret_key=secret_key,
    passphrase=passphrase,
    base_url=base_url
)

# Get open positions
try:
    positions = client.get_positions()
    
    if not positions or len(positions) == 0:
        print("✅ No open positions to close.")
    else:
        print(f"📊 Found {len(positions)} open position(s) to close:\n")
        
        for i, pos in enumerate(positions, 1):
            symbol = pos.get('instId')
            position_size = float(pos.get('positions', 0))
            position_side = pos.get('positionSide', 'net')
            margin_mode = pos.get('marginMode', 'cross')
            avg_price = pos.get('averagePrice')
            mark_price = pos.get('markPrice')
            unrealized_pnl = pos.get('unrealizedPnl')
            
            print(f"Position #{i}: {symbol}")
            print(f"  Size: {position_size} contracts")
            print(f"  Entry: ${avg_price}")
            print(f"  Current: ${mark_price}")
            print(f"  P&L: ${unrealized_pnl}")
            print()
            
            # Determine close side (opposite of position)
            # For net positions (one-way mode), we close by selling if we're long
            # Since position_size is positive for long positions, we sell to close
            if position_size > 0:
                close_side = "sell"
                print(f"  → Closing LONG position with SELL order")
            else:
                close_side = "buy"
                print(f"  → Closing SHORT position with BUY order")
                position_size = abs(position_size)
            
            # Place market order to close
            print(f"\n  Placing market {close_side} order for {position_size} contracts...")
            
            try:
                result = client.place_market_order(
                    symbol=symbol,
                    side=close_side,
                    size=position_size,
                    trade_mode=margin_mode
                )
                
                print(f"  ✅ Position closed successfully!")
                print(f"  Order ID: {result.get('order_id')}")
                print(f"  Realized P&L: ${unrealized_pnl}")
                print()
                
            except Exception as e:
                print(f"  ❌ Failed to close position: {e}")
                import traceback
                traceback.print_exc()
            
            print("-" * 80)
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
