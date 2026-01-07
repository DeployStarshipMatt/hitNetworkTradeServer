"""
Check contract value definitions for different pairs
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

# Get instrument details
instruments = client._request("GET", "/api/v1/market/instruments", {"instType": "SWAP"})

print("Contract Specifications:\n")

for symbol in ['BTC-USDT', 'ETH-USDT', 'ATOM-USDT']:
    for inst in instruments:
        if inst.get('instId') == symbol:
            print(f"{symbol}:")
            print(f"  Contract Value (ctVal): {inst.get('ctVal')}")
            print(f"  Contract Type: {inst.get('contractType')}")
            print(f"  Min Size: {inst.get('minSize')}")
            print(f"  Lot Size: {inst.get('lotSize')}")
            
            ct_val = inst.get('ctVal')
            lot_size = float(inst.get('lotSize', 1))
            
            if ct_val:
                print(f"  ✅ 1 contract = {ct_val} {symbol.split('-')[0]}")
                print(f"  Min trade = {lot_size} × {ct_val} = {float(lot_size) * float(ct_val)} {symbol.split('-')[0]}")
            else:
                print(f"  Contract Value: Not specified (likely 1 contract = 1 {symbol.split('-')[0]})")
                print(f"  OR: 1 contract = $1 USD (need to test)")
            print()
            break

print("\nLet me check the actual ATOM position to verify:")
positions = client._request("GET", "/api/v1/account/positions")

for pos in positions:
    if pos.get('instId') == 'ATOM-USDT':
        positions_val = pos.get('positions')
        avg_price = float(pos.get('averagePrice', 0))
        initial_margin = float(pos.get('initialMargin', 0))
        leverage = float(pos.get('leverage', 1))
        
        print(f"ATOM Position:")
        print(f"  Positions field: {positions_val}")
        print(f"  Average Price: ${avg_price}")
        print(f"  Initial Margin: ${initial_margin}")
        print(f"  Leverage: {leverage}x")
        print()
        
        positions_num = abs(float(positions_val))
        
        print(f"Scenario A: If 'positions: {positions_val}' means {positions_num} ATOM tokens:")
        notional_a = positions_num * avg_price
        margin_a = notional_a / leverage
        print(f"  Notional = {positions_num} × ${avg_price} = ${notional_a}")
        print(f"  Required margin = ${notional_a} / {leverage} = ${margin_a}")
        print(f"  Match? {abs(margin_a - initial_margin) < 0.01}")
        print()
        
        print(f"Scenario B: If 'positions: {positions_val}' means ${positions_num} USD exposure:")
        notional_b = positions_num
        margin_b = notional_b / leverage
        print(f"  Notional = ${positions_num}")
        print(f"  Required margin = ${positions_num} / {leverage} = ${margin_b}")
        print(f"  Match? {abs(margin_b - initial_margin) < 0.01}")
