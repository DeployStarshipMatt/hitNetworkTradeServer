"""
Check account balance and figure out actual BTC trade size
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

# Get balance
balance_data = client._request("GET", "/api/v1/account/balance")
if isinstance(balance_data, list) and len(balance_data) > 0:
    balance = float(balance_data[0].get('availableBalance', 0))
else:
    balance = float(balance_data.get('availableBalance', 50))
print(f"Current Account Balance: ${balance}")
print()

# If we started with $50 and have this much now, what was the P&L?
starting_balance = 50
current_balance = balance
pnl = current_balance - starting_balance

print(f"Starting balance: ${starting_balance}")
print(f"Current balance: ${current_balance}")
print(f"P&L from trades: ${pnl:.2f}")
print()

# Now let's think about the BTC trade
print("BTC Trade Analysis:")
print("Size shown: 0.1 contracts")
print()

# Theory: Size represents USD value, not BTC quantity
print("Theory 1: Size = USD value")
print("  0.1 contracts = $0.10 USD exposure")
print("  With max leverage (100x), margin = $0.001")
print("  ✅ Fits in $50 account")
print()

print("Theory 2: Size = BTC quantity")
print("  0.1 contracts = 0.1 BTC")
print("  At BTC = $95,000, notional = $9,500")
print("  With max leverage (100x), margin = $95")
print("  ❌ Exceeds $50 account balance")
print()

# Check if the lot size is actually in USD
print("Let me check ATOM to verify:")
print(f"  ATOM position: 3 contracts")
print(f"  ATOM price: $2.414")
print(f"  Margin used: $3.62")
print()

print("If 1 contract = 1 ATOM:")
print(f"  Notional = 3 × $2.414 = ${3 * 2.414}")
print(f"  Margin (2x lev) = ${3 * 2.414 / 2:.2f}")
print(f"  ✅ Matches actual margin $3.62")
print()

print("If 1 contract = $1 USD:")
print(f"  Notional = $3")
print(f"  Margin (2x lev) = $1.50")
print(f"  ❌ Doesn't match actual margin $3.62")
print()

print("CONCLUSION:")
print("  ATOM: 1 contract = 1 ATOM (coin-based)")
print("  BTC: Need to determine if different...")
print()

# The key is: what's the minimum USD value you can trade?
print("Possible explanation:")
print("  BTC lot size 0.1 might mean you can trade in $0.10 increments")
print("  NOT 0.1 BTC increments")
print("  This would allow small trades on a $50 account")
