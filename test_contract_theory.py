"""
Test: What does "size" actually mean in BloFin orders?
Check if it's USD value or coin quantity
"""
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

# Check ATOM position details
print("Current ATOM Position:")
print("  Size shown: -3 contracts")
print("  Initial Margin: $3.62")
print("  Entry Price: $2.414")
print("  Leverage: 2x")
print()

print("Testing Theory 1: 1 contract = $1 USD")
print(f"  3 contracts = $3 exposure")
print(f"  Margin needed (2x leverage) = $3 / 2 = $1.50")
print(f"  ❌ Doesn't match actual margin of $3.62")
print()

print("Testing Theory 2: 1 contract = 1 ATOM token")
print(f"  3 contracts = 3 ATOM")
print(f"  Notional = 3 × $2.414 = $7.242")
print(f"  Margin needed (2x leverage) = $7.242 / 2 = $3.621")
print(f"  ✅ Matches actual margin of $3.62!")
print()

# Get current market price for BTC
instruments = client._request("GET", "/api/v1/market/instruments", {"instType": "SWAP"})
for inst in instruments:
    if inst.get('instId') == 'BTC-USDT':
        print(f"BTC-USDT Info:")
        print(f"  Min Size: {inst.get('minSize')}")
        print(f"  Lot Size: {inst.get('lotSize')}")
        
        # Get current ticker
        ticker = client._request("GET", "/api/v1/market/ticker", {"instId": "BTC-USDT"})
        if ticker:
            btc_price = float(ticker[0].get('last', 0))
            print(f"  Current BTC Price: ${btc_price:,.2f}")
            print()
            print(f"If 1 contract = 1 BTC:")
            print(f"  1 contract = ${btc_price:,.2f}")
            print()
            print(f"If 1 contract = 0.1 BTC (lot size):")
            print(f"  1 contract = ${btc_price * 0.1:,.2f}")
            print()
            print(f"If 1 contract = $1 USD:")
            print(f"  To get $1 exposure: 1 contract")
            print(f"  To get $100 exposure: 100 contracts")
        break
