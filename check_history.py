import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'trading-server'))

from blofin_client import BloFinClient
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# Get order history (last 7 days)
from datetime import datetime, timedelta
end_time = int(datetime.now().timestamp() * 1000)
start_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)

result = client._request('GET', f'/api/v1/trade/orders-history?instType=SWAP&startTime={start_time}&endTime={end_time}')

if result and 'data' in result:
    orders = result['data']
    print(f"Total orders (last 7 days): {len(orders)}\n")
    
    # Filter filled orders and group by symbol
    closed_trades = {}
    for order in orders:
        if order.get('state') == 'filled':
            symbol = order.get('instId')
            side = order.get('side')
            size = float(order.get('filledSize', 0))
            avg_price = float(order.get('avgFillPrice', 0))
            fee = float(order.get('fee', 0))
            timestamp = order.get('updateTime', order.get('createTime'))
            
            if symbol not in closed_trades:
                closed_trades[symbol] = []
            closed_trades[symbol].append({
                'side': side,
                'size': size,
                'price': avg_price,
                'fee': fee,
                'time': timestamp
            })
    
    print("Closed trades by pair:")
    print("=" * 80)
    
    total_pnl = 0
    for symbol, trades in closed_trades.items():
        # Try to match buys and sells
        buys = [t for t in trades if t['side'] == 'buy']
        sells = [t for t in trades if t['side'] == 'sell']
        
        if buys and sells:
            # Calculate PnL for matched trades
            buy_total = sum(t['size'] * t['price'] for t in buys)
            sell_total = sum(t['size'] * t['price'] for t in sells)
            fees = sum(t['fee'] for t in trades)
            pnl = sell_total - buy_total - fees
            
            status = "PROFIT" if pnl > 0 else "LOSS"
            print(f"{symbol:15} | PnL: ${pnl:>10.2f} | {status:6} | Orders: {len(trades)}")
            total_pnl += pnl
    
    print("=" * 80)
    print(f"Total Realized PnL (last 7 days): ${total_pnl:.2f}")
else:
    print('No order history found')
