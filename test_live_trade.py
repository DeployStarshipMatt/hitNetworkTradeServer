"""
Test live trade execution with minimal position size.
Simulates Discord bot sending a signal to the trading server.
"""
import requests
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'trading-server'))
from blofin_client import BloFinClient
from dotenv import load_dotenv

load_dotenv()

# Configuration
TRADING_SERVER_URL = "http://167.172.20.242:8000"
API_KEY = "hNa8xKm4PqWr9tYvBc2FgJl5ZsXw7Dp3"

# Initialize BloFin client to get live price
blofin_client = BloFinClient(
    api_key=os.getenv('BLOFIN_API_KEY'),
    secret_key=os.getenv('BLOFIN_SECRET_KEY'),
    passphrase=os.getenv('BLOFIN_PASSPHRASE'),
    base_url=os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')
)

# Get current BTC price from BloFin API
def get_btc_price():
    """Get current BTC price from BloFin ticker."""
    try:
        print("\n🔍 Fetching live BTC price from BloFin...")
        ticker = blofin_client.get_ticker("BTC-USDT")
        if ticker and 'last' in ticker:
            price = float(ticker['last'])
            print(f"✅ Live BTC price: ${price:,.2f}")
            return price
        else:
            print("⚠️ Could not fetch price, using fallback $95,000")
            return 95000.0
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        print("⚠️ Using fallback price: $95,000")
        return 95000.0

# Create a minimal test signal
btc_price = get_btc_price()
entry = btc_price
stop_loss = entry * 0.98  # 2% stop loss
tp1 = entry * 1.01  # 1% take profit
tp2 = entry * 1.015  # 1.5% take profit
tp3 = entry * 1.02  # 2% take profit

test_signal = {
    "symbol": "BTC-USDT",
    "side": "long",
    "entry_price": entry,
    "stop_loss": stop_loss,
    "take_profit": tp1,
    "take_profit_2": tp2,
    "take_profit_3": tp3,
    "size": None,  # Let server calculate based on 1% risk
    "leverage": 10,
    "source": "test",
    "signal_id": f"test_{int(datetime.utcnow().timestamp())}",
    "timestamp": datetime.utcnow().isoformat(),
    "raw_message": "TEST TRADE - Minimal size"
}

print("\n" + "="*60)
print("🧪 LIVE TRADE TEST")
print("="*60)
print(f"\n📊 Signal Details:")
print(f"  Symbol: {test_signal['symbol']}")
print(f"  Side: {test_signal['side'].upper()}")
print(f"  Entry: ${entry:.2f}")
print(f"  Stop Loss: ${stop_loss:.2f} (-2%)")
print(f"  TP1: ${tp1:.2f} (+1%)")
print(f"  TP2: ${tp2:.2f} (+1.5%)")
print(f"  TP3: ${tp3:.2f} (+2%)")
print(f"  Leverage: {test_signal['leverage']}x")
print(f"\n⚠️  Risk: 1% of account (~$5)")

input("\n⚡ Press ENTER to execute the trade (or Ctrl+C to cancel)...")

# Send signal to trading server
print("\n📤 Sending signal to trading server...")
try:
    response = requests.post(
        f"{TRADING_SERVER_URL}/api/v1/trade",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json=test_signal,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    result = response.json()
    print(f"\n📋 Response:")
    print(json.dumps(result, indent=2))
    
    if response.status_code == 200 and result.get('success'):
        print("\n✅ TRADE EXECUTED SUCCESSFULLY!")
        print(f"   Order ID: {result.get('order_id', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
    else:
        print("\n❌ TRADE FAILED!")
        print(f"   Error: {result.get('message', 'Unknown error')}")
        
except requests.exceptions.Timeout:
    print("\n❌ Request timed out - server may be processing")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
print("Check your Blofin account and Discord webhook for confirmation")
print("="*60)
