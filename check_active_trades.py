"""
Check for active trades in copy trading account
"""
import os
import sys
from dotenv import load_dotenv

# Add trading-server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trading-server'))

from blofin_client import BloFinClient

def main():
    load_dotenv()
    
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE'),
        base_url=os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')
    )
    
    print("🔍 Checking Copy Trading Account Status")
    print("=" * 70)
    
    # Check Balance
    print("\n💰 Account Balance:")
    balance = client.get_account_balance()
    total_equity = float(balance.get('totalEquity', 0))
    print(f"   Total Equity: ${total_equity:.2f}")
    
    for detail in balance.get('details', []):
        currency = detail['currency']
        equity = float(detail['equity'])
        available = float(detail['available'])
        frozen = float(detail.get('frozen', 0))
        print(f"   {currency}:")
        print(f"     - Equity: ${equity:.2f}")
        print(f"     - Available: ${available:.2f}")
        print(f"     - Frozen: ${frozen:.2f}")
    
    # Check Positions (By Contract)
    print("\n📊 Open Positions (By Contract):")
    positions = client.get_positions()
    
    if not positions:
        print("   ✅ No open positions")
    else:
        print(f"   Found {len(positions)} position(s):\n")
        for pos in positions:
            inst_id = pos.get('instId')
            position_size = float(pos.get('positions', 0))
            avg_price = float(pos.get('averagePrice', 0))
            mark_price = float(pos.get('markPrice', 0))
            unrealized_pnl = float(pos.get('unrealizedPnl', 0))
            leverage = pos.get('leverage')
            margin_mode = pos.get('marginMode')
            
            side = "LONG" if position_size > 0 else "SHORT"
            
            print(f"   {inst_id} ({side}):")
            print(f"     - Size: {abs(position_size)}")
            print(f"     - Entry: ${avg_price}")
            print(f"     - Mark: ${mark_price}")
            print(f"     - PnL: ${unrealized_pnl:.2f}")
            print(f"     - Leverage: {leverage}x ({margin_mode})")
            print()
    
    # Check Pending Orders
    print("\n📋 Pending Orders:")
    try:
        pending = client._request("GET", "/api/v1/copytrading/trade/orders-pending")
        if not pending:
            print("   ✅ No pending orders")
        else:
            print(f"   Found {len(pending)} pending order(s):\n")
            for order in pending[:5]:  # Show first 5
                print(f"   {order.get('instId')} - {order.get('side')} {order.get('size')} @ ${order.get('price')}")
                print(f"     Status: {order.get('state')}, Type: {order.get('orderType')}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch pending orders: {e}")
    
    # Check Pending TPSL (By Contract)
    print("\n🎯 Pending TP/SL Orders (By Contract):")
    try:
        tpsl_orders = client._request("GET", "/api/v1/copytrading/trade/pending-tpsl-by-contract")
        if not tpsl_orders:
            print("   ✅ No pending TP/SL orders")
        else:
            print(f"   Found {len(tpsl_orders)} TP/SL order(s):\n")
            for order in tpsl_orders:
                inst_id = order.get('instId')
                tp = order.get('tpTriggerPrice', 'N/A')
                sl = order.get('slTriggerPrice', 'N/A')
                size = order.get('size')
                state = order.get('state')
                
                print(f"   {inst_id}:")
                if tp and tp != 'N/A':
                    print(f"     - Take Profit: ${tp}")
                if sl and sl != 'N/A':
                    print(f"     - Stop Loss: ${sl}")
                print(f"     - Size: {size}, State: {state}")
                print()
    except Exception as e:
        print(f"   ⚠️  Could not fetch TP/SL orders: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Account Check Complete")

if __name__ == "__main__":
    main()
