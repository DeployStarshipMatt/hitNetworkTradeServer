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
print("ACTUAL CURRENT POSITION")
print("=" * 60)

# Try ALL position endpoints
print("\n1. Regular /api/v1/trade/position-risk:")
try:
    pos_risk = client._request("GET", "/api/v1/trade/position-risk", {"instId": "BTC-USDT"})
    print(f"Result: {pos_risk}")
except Exception as e:
    print(f"Error: {e}")

print("\n2. Copytrading account balance (shows margin used):")
try:
    balance = client.get_account_balance()
    print(f"Total Equity: ${balance.get('totalEquity')}")
    print(f"Available: ${balance.get('availableBalance')}")
    print(f"Margin Used: ${float(balance.get('totalEquity', 0)) - float(balance.get('availableBalance', 0)):.2f}")
except Exception as e:
    print(f"Error: {e}")

print("\n3. Check /api/v1/account/positions:")
try:
    positions = client._request("GET", "/api/v1/account/positions")
    print(f"Result: {positions}")
    if positions and isinstance(positions, list):
        for pos in positions:
            if pos.get('instId') == 'BTC-USDT':
                print(f"\n  BTC Position Found:")
                print(f"    Contracts: {pos.get('contracts')}")
                print(f"    Position Side: {pos.get('positionSide')}")
                print(f"    Unrealized PnL: {pos.get('unrealizedPnl')}")
except Exception as e:
    print(f"Error: {e}")

print("\n4. Get all fills to calculate net position:")
try:
    fills = client._request("GET", "/api/v1/copytrading/trade/fills", {"instId": "BTC-USDT"})
    print(f"Fills: {fills}")
    
    if fills and isinstance(fills, list):
        total_buys = 0
        total_sells = 0
        
        for fill in fills[:20]:  # Last 20 fills
            side = fill.get('side')
            size = float(fill.get('size', 0))
            if side == 'buy':
                total_buys += size
            elif side == 'sell':
                total_sells += size
        
        net_position = total_buys - total_sells
        print(f"\nCalculated from fills:")
        print(f"  Total Buys: {total_buys} contracts")
        print(f"  Total Sells: {total_sells} contracts")
        print(f"  Net Position: {net_position} contracts")
        print(f"  Actual BTC: {net_position * 0.001:.6f} BTC")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
