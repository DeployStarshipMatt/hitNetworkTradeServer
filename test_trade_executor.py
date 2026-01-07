"""
Test the reusable trade executor with SEI signal
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "trading-server"))

from blofin_client import BloFinClient
from trade_executor import TradeExecutor
from dotenv import load_dotenv
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Initialize
client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE')
)

executor = TradeExecutor(client)

# SEI Signal from Discord
# We already have 1 SEI short, so let's test the calculation only
print("Testing position size calculation for SEI signal...")
print()

symbol = "SEI-USDT"
entry = 0.125294  # Signal entry
stop_loss = 0.127698
tp1 = 0.123615

# Calculate what the position size SHOULD be for 1% risk
size_info = client.calculate_position_size(
    symbol=symbol,
    entry_price=entry,
    stop_loss=stop_loss,
    risk_percent=1.0
)

print(f"SEI/USDT SHORT Signal Analysis:")
print(f"  Entry: ${entry}")
print(f"  Stop Loss: ${stop_loss}")
print(f"  TP1: ${tp1}")
print()
print(f"Risk Management (1%):")
print(f"  Available Balance: ${size_info['available_balance']:.2f}")
print(f"  Risk Amount: ${size_info['risk_amount']:.4f}")
print(f"  Risk per SEI: ${size_info['risk_per_unit']:.6f}")
print(f"  Calculated Size: {size_info['size']} SEI (from {size_info['raw_size']:.2f})")
print(f"  Notional Value: ${size_info['notional_value']:.2f}")
print(f"  Margin @ 2x: ${size_info['margin_needed']:.2f}")
print()

# Now check ATOM calculation
print("=" * 60)
print("Checking ATOM trade that lost $4...")
print()

# ATOM trade details (from earlier)
atom_entry = 2.414
atom_sl = 2.546
atom_size = 3  # What we used

# What SHOULD the size have been?
atom_size_info = client.calculate_position_size(
    symbol="ATOM-USDT",
    entry_price=atom_entry,
    stop_loss=atom_sl,
    risk_percent=1.0
)

print(f"ATOM/USDT SHORT Analysis:")
print(f"  Entry: ${atom_entry}")
print(f"  Stop Loss: ${atom_sl}")
print(f"  Risk per ATOM: ${abs(atom_entry - atom_sl):.6f}")
print()
print(f"What we USED:")
print(f"  Size: {atom_size} ATOM")
print(f"  Risk: ${atom_size * abs(atom_entry - atom_sl):.4f} ({(atom_size * abs(atom_entry - atom_sl) / size_info['available_balance'] * 100):.2f}%)")
print()
print(f"What we SHOULD have used (1% risk):")
print(f"  Size: {atom_size_info['size']} ATOM")
print(f"  Risk: ${atom_size_info['risk_amount']:.4f} (1.00%)")
print(f"  Margin @ 2x: ${atom_size_info['margin_needed']:.2f}")
print()
print(f"DIFFERENCE:")
print(f"  We used {atom_size} instead of {atom_size_info['size']}")
print(f"  We risked ${atom_size * abs(atom_entry - atom_sl):.2f} instead of ${atom_size_info['risk_amount']:.2f}")
print(f"  That's {atom_size / atom_size_info['size']:.1f}x more risk than we should have!")
