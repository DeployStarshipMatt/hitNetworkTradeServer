"""
Trading CLI Tool

Simple command-line interface for common trading tasks.
Use this instead of creating individual scripts.

Usage examples:
  python trade_cli.py status                    # Show account summary
  python trade_cli.py position ATOM-USDT        # Show specific position
  python trade_cli.py close BTC-USDT            # Close a position
  python trade_cli.py protect ATOM-USDT 2.546 2.354 2.281 2.217  # Set SL + 3-tier TP
  python trade_cli.py execute SEI-USDT short 0.125 0.128 0.123   # Execute new trade
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from trading_utils import *
from trade_executor import TradeExecutor
from dotenv import load_dotenv
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

load_dotenv()


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    # Initialize client
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE')
    )
    
    command = sys.argv[1].lower()
    
    try:
        if command == "status":
            # Show full account summary
            get_account_summary(client)
        
        elif command == "position":
            # Show specific position with protection
            if len(sys.argv) < 3:
                print("Usage: python trade_cli.py position SYMBOL")
                return
            symbol = sys.argv[2].upper()
            print_position_summary(client, symbol)
            print_algo_orders(client, symbol)
        
        elif command == "close":
            # Close a position
            if len(sys.argv) < 3:
                print("Usage: python trade_cli.py close SYMBOL")
                return
            symbol = sys.argv[2].upper()
            confirm = input(f"Close {symbol} position? (yes/no): ")
            if confirm.lower() == 'yes':
                result = close_position(client, symbol)
                print(f"Position closed: {result}")
            else:
                print("Canceled")
        
        elif command == "protect":
            # Set SL/TP on existing position
            if len(sys.argv) < 5:
                print("Usage: python trade_cli.py protect SYMBOL SL TP1 [TP2] [TP3]")
                print("Example: python trade_cli.py protect ATOM-USDT 2.546 2.354 2.281 2.217")
                return
            
            symbol = sys.argv[2].upper()
            sl = float(sys.argv[3])
            tp1 = float(sys.argv[4])
            tp2 = float(sys.argv[5]) if len(sys.argv) > 5 else None
            tp3 = float(sys.argv[6]) if len(sys.argv) > 6 else None
            
            fix_position_protection(client, symbol, sl, tp1, tp2, tp3)
        
        elif command == "execute":
            # Execute new trade
            if len(sys.argv) < 6:
                print("Usage: python trade_cli.py execute SYMBOL SIDE ENTRY SL TP1 [TP2] [TP3]")
                print("Example: python trade_cli.py execute SEI-USDT short 0.125 0.128 0.123")
                return
            
            symbol = sys.argv[2].upper()
            side = sys.argv[3].lower()
            entry = float(sys.argv[4])
            sl = float(sys.argv[5])
            tp1 = float(sys.argv[6])
            tp2 = float(sys.argv[7]) if len(sys.argv) > 7 else None
            tp3 = float(sys.argv[8]) if len(sys.argv) > 8 else None
            
            executor = TradeExecutor(client)
            
            # Confirm trade
            print(f"\nTrade Plan:")
            print(f"  {symbol} {side.upper()}")
            print(f"  Entry: ${entry}")
            print(f"  Stop Loss: ${sl}")
            print(f"  TP1: ${tp1}")
            if tp2 and tp3:
                print(f"  TP2: ${tp2}")
                print(f"  TP3: ${tp3}")
            
            # Calculate position size
            size_info = client.calculate_position_size(symbol, entry, sl, risk_percent=1.0)
            print(f"\nPosition Size: {size_info['size']} (1% risk)")
            print(f"Margin Needed: ${size_info['margin_needed']:.2f}")
            
            confirm = input("\nExecute trade? (yes/no): ")
            if confirm.lower() == 'yes':
                use_3tier = tp2 is not None and tp3 is not None
                result = executor.execute_trade(
                    symbol=symbol,
                    side=side,
                    entry_price=entry,
                    stop_loss=sl,
                    take_profit=tp1,
                    risk_percent=1.0,
                    use_3tier_tp=use_3tier
                )
                if result['success']:
                    print("\n✓ Trade executed successfully!")
                else:
                    print(f"\n✗ Trade failed: {result.get('error')}")
            else:
                print("Canceled")
        
        elif command == "cancel":
            # Cancel algo orders
            if len(sys.argv) < 3:
                print("Usage: python trade_cli.py cancel SYMBOL [algo_id]")
                print("  Omit algo_id to cancel all orders for symbol")
                return
            
            symbol = sys.argv[2].upper()
            
            if len(sys.argv) > 3:
                # Cancel specific order
                algo_id = sys.argv[3]
                if cancel_algo_order(client, symbol, algo_id):
                    print(f"Canceled algo order {algo_id}")
                else:
                    print(f"Failed to cancel {algo_id}")
            else:
                # Cancel all orders
                canceled = cancel_all_algo_orders(client, symbol)
                print(f"Canceled {canceled} algo orders for {symbol}")
        
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
