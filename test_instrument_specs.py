"""
Test the improved instrument checking and size rounding
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

print("Testing Instrument Info and Size Rounding:")
print("=" * 60)

# Test different symbols
symbols = ['BTC-USDT', 'ETH-USDT', 'ATOM-USDT']

for symbol in symbols:
    print(f"\n{symbol}:")
    spec = client.get_instrument_info(symbol)
    print(f"  Min Size: {spec['minSize']}")
    print(f"  Lot Size: {spec['lotSize']}")
    
    # Test various size rounding scenarios
    test_sizes = [0.05, 0.1, 0.5, 1.0, 1.5, 2.3, 3.7, 10.0]
    
    print(f"\n  Size Rounding Tests:")
    for test_size in test_sizes:
        rounded = client.round_size_to_lot(symbol, test_size)
        print(f"    {test_size} → {rounded}")

print("\n" + "=" * 60)
print("\nCache check - second call should be instant (no API call):")
for symbol in symbols:
    spec = client.get_instrument_info(symbol)
    print(f"  {symbol}: cached={symbol in client._instrument_cache}")

print(f"\nAPI calls made: {client.stats['api_calls']}")
print("✅ Test complete!")
