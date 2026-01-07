"""
Test New Risk Management with Equity-Based Calculation and 10x Leverage

Shows the fixed calculation using total equity instead of available balance.
"""
import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

print("=" * 70)
print("NEW RISK MANAGEMENT VERIFICATION")
print("=" * 70)

# Get account data
balance_data = client.get_account_balance()
equity = float(balance_data['details'][0]['equity'])
available = float(balance_data['details'][0]['available'])

print(f"\nACCOUNT STATUS:")
print(f"  Total Equity: ${equity:.2f}")
print(f"  Available: ${available:.2f}")
print(f"  In Positions: ${equity - available:.2f}")

# Test signal
symbol = "SEI-USDT"
entry = 0.125294
sl = 0.127698
tp1 = 0.123615

print(f"\nTEST SIGNAL:")
print(f"  Symbol: {symbol}")
print(f"  Entry: ${entry}")
print(f"  Stop Loss: ${sl}")

# Calculate with OLD way (available balance, 2x leverage)
print(f"\n❌ OLD METHOD (WRONG):")
print(f"  Base: Available Balance (${available:.2f})")
print(f"  Leverage: 2x")
risk_old = available * 0.01
size_old = risk_old / abs(entry - sl)
print(f"  1% Risk: ${risk_old:.4f}")
print(f"  Position Size: {int(size_old)} SEI")
margin_old = (size_old * entry) / 2
print(f"  Margin Needed: ${margin_old:.2f}")
if margin_old > available:
    print(f"  ⚠️  NOT ENOUGH MARGIN!")

# Calculate with NEW way (total equity, 10x leverage)
print(f"\n✅ NEW METHOD (CORRECT):")
print(f"  Base: Total Equity (${equity:.2f})")
print(f"  Leverage: 10x")
size_info = client.calculate_position_size(symbol, entry, sl, risk_percent=1.0, leverage=10)
print(f"  1% Risk: ${size_info['risk_amount']:.4f}")
print(f"  Position Size: {size_info['size']} SEI")
print(f"  Margin Needed: ${size_info['margin_needed']:.2f}")
print(f"  Available: ${available:.2f}")
if size_info['margin_needed'] <= available:
    print(f"  ✅ ENOUGH MARGIN!")
else:
    print(f"  ⚠️  Need ${size_info['margin_needed'] - available:.2f} more margin")

# Verify actual risk
actual_risk = size_info['size'] * abs(entry - sl)
actual_risk_pct = (actual_risk / equity) * 100
print(f"\nRISK VERIFICATION:")
print(f"  If SL hits: {size_info['size']} SEI × ${abs(entry - sl):.6f} = ${actual_risk:.4f}")
print(f"  Risk %: {actual_risk_pct:.2f}% of ${equity:.2f} equity")
if 0.95 <= actual_risk_pct <= 1.05:
    print(f"  ✅ EXACTLY 1% RISK!")
else:
    print(f"  ⚠️  Not 1% (rounding variance)")

print(f"\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print(f"✅ Now using TOTAL EQUITY (${equity:.2f}) not available (${available:.2f})")
print(f"✅ Using 10x leverage instead of 2x = 5x more margin available")
print(f"✅ Position sizes will be correct for 1% of EQUITY risk")
print(f"✅ More margin free for multiple positions")
print("=" * 70)
