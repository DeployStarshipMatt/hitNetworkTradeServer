"""Check SEI-USDT availability"""
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

# Check if SEI-USDT exists
info = client.get_instrument_info("SEI-USDT")
print("Instrument Info:")
print(info)

# Get ticker for current price
import requests
response = requests.get("https://openapi.blofin.com/api/v1/market/tickers?instId=SEI-USDT")
print("\nTicker Data:")
print(response.json())

# Check if we have positions
positions = client.get_positions()
print("\nCurrent Positions:")
print(positions)
