"""Calculate SEI trade with current price"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from dotenv import load_dotenv
import os

load_dotenv()

client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

# Get balance
balance = client.get_account_balance()
print("Account Balance:")
print(balance)
print()

# Calculate for SEI
entry = 0.1244  # Current market price
stop_loss = 0.127698
size = 210  # SEI tokens

notional_value = size * entry
margin_needed_35x = notional_value / 35

print(f"Trade Calculation:")
print(f"  Size: {size} SEI")
print(f"  Entry Price: ${entry}")
print(f"  Notional Value: ${notional_value:.2f}")
print(f"  Margin @ 35x: ${margin_needed_35x:.4f}")
print(f"  Margin @ 2x: ${notional_value / 2:.4f}")

# Try with smaller size
sizes_to_test = [210, 100, 50, 20, 10]
for test_size in sizes_to_test:
    notional = test_size * entry
    margin_2x = notional / 2
    print(f"\n  {test_size} SEI: Notional=${notional:.2f}, Margin@2x=${margin_2x:.4f}")
