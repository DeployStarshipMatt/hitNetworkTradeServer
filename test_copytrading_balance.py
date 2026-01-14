"""
Test copy trading account balance endpoint
"""
import os
import sys
from dotenv import load_dotenv

# Add trading-server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trading-server'))

from blofin_client import BloFinClient

def main():
    load_dotenv()
    
    client = BloFinClient(
        api_key=os.getenv('BLOFIN_API_KEY'),
        secret_key=os.getenv('BLOFIN_SECRET_KEY'),
        passphrase=os.getenv('BLOFIN_PASSPHRASE'),
        base_url=os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')
    )
    
    print("Testing Copy Trading Balance Endpoint...")
    print("=" * 60)
    
    # Test copy trading balance endpoint
    try:
        response = client._request("GET", "/api/v1/copytrading/account/balance")
        print("\n✅ Copy Trading Balance Response:")
        print(f"Total Equity: ${response['totalEquity']}")
        print(f"Details: {response['details']}")
        
        if response['details']:
            for detail in response['details']:
                print(f"\nCurrency: {detail['currency']}")
                print(f"  Equity: {detail['equity']}")
                print(f"  Available: {detail['available']}")
        
    except Exception as e:
        print(f"\n❌ Copy Trading Balance Failed: {e}")
    
    print("\n" + "=" * 60)
    print("\nTesting Regular Futures Balance Endpoint (for comparison)...")
    print("=" * 60)
    
    # Test regular futures balance for comparison
    try:
        response = client._request("GET", "/api/v1/account/balance")
        print("\n✅ Regular Futures Balance Response:")
        print(f"Total Equity: ${response['totalEquity']}")
        print(f"Details: {response['details']}")
        
        if response['details']:
            for detail in response['details']:
                print(f"\nCurrency: {detail['currency']}")
                print(f"  Equity: {detail['equity']}")
                print(f"  Available: {detail['available']}")
        
    except Exception as e:
        print(f"\n❌ Regular Balance Failed: {e}")

if __name__ == "__main__":
    main()
