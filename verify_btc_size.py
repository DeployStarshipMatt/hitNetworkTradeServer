#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv
sys.path.append('trading-server')
from blofin_client import BloFinClient

load_dotenv()
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 60)
print("BTC POSITION SIZE BREAKDOWN")
print("=" * 60)

# Get instrument specs
specs = client.get_instrument_info("BTC-USDT")
contract_value = 0.001  # BTC per contract (standard for BTC-USDT)
print(f"\nBTC-USDT Contract Specs:")
print(f"  Contract Value: {contract_value} BTC per contract")
print(f"  Min Size: {specs.get('minSize')}")
print(f"  Lot Size: {specs.get('lotSize')}")

# Try to get copytrading balance for context
try:
    balance = client.get_account_balance()
    print(f"\nCopytrading Account:")
    print(f"  Total Equity: ${balance.get('totalEquity', 0)}")
    print(f"  Available: ${balance.get('availableBalance', 0)}")
except Exception as e:
    print(f"Error getting balance: {e}")

# Check order history to see actual sizes
print("\n" + "=" * 60)
print("RECENT BTC ORDER HISTORY:")
print("=" * 60)
try:
    history = client._request("GET", "/api/v1/copytrading/trade/orders-history", {
        "instId": "BTC-USDT"
    })
    
    if history and isinstance(history, list):
        for order in history[:10]:  # Last 10 orders
            order_id = order.get('orderId')
            side = order.get('side')
            size = order.get('size')
            filled_size = order.get('filledSize', size)
            state = order.get('state')
            avg_price = order.get('avgFillPrice', 0)
            
            # Calculate actual BTC amount
            btc_amount = float(filled_size) * contract_value
            notional_usd = btc_amount * float(avg_price) if avg_price else 0
            
            print(f"\n{side.upper()} Order {order_id} - {state}")
            print(f"  Contracts: {filled_size}")
            print(f"  Actual BTC: {btc_amount:.6f} BTC")
            print(f"  Price: ${avg_price}")
            print(f"  Notional: ${notional_usd:.2f}")
    else:
        print("No history found")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("  5.2 contracts = 5.2 × 0.001 = 0.0052 BTC")
print(f"  At $94,000/BTC ≈ $488.80 notional")
print("=" * 60)
