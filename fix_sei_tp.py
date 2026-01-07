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

# We have 1 SEI total with only TP1 set
# Need to cancel existing TP1 and set 3 TPs for partial closes

print("Canceling existing TP1...")
try:
    cancel_result = client._request("POST", "/api/v1/trade/cancel-algo", {
        "instId": "SEI-USDT",
        "algoId": "10002575787"
    })
    print(f"  Canceled: {cancel_result.get('code')}")
except Exception as e:
    print(f"  Error: {e}")

# For 1 SEI position, we can't do 3-tier properly (would need 0.33 each)
# But SEI requires whole numbers (lotSize=1)
# Best we can do is set all 3 TPs for the full 1 SEI at different levels
# Or just keep TP1 as the single target

print("\nSince we only have 1 SEI (can't split), setting single TP at TP1:")
tp1 = 0.123615

tp1_result = client.set_take_profit("SEI-USDT", "buy", tp1, 1)
print(f"  TP1: 1 SEI @ ${tp1} - {tp1_result['order_id']}")

print("\nNote: Position is only 1 SEI due to earlier API errors.")
print("Unable to add more to position (API keeps rejecting with 'All operations failed')")
print("Current protection: SL @ $0.127698, TP @ $0.123615")
