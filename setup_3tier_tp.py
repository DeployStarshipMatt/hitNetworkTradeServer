"""
Cancel current TPs and set up 3-tier take profit system
TP1: 1 contract at closest target
TP2: 1 contract at mid target  
TP3: 1 contract at furthest target
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

SYMBOL = "ATOM-USDT"
ENTRY = 2.414

# Original TP from signal
TP_FINAL = 2.354262

# Calculate 3 TP levels (evenly spaced)
price_range = ENTRY - TP_FINAL  # 0.059738
TP1 = round(ENTRY - (price_range * 0.33), 6)  # 33% of the way
TP2 = round(ENTRY - (price_range * 0.66), 6)  # 66% of the way
TP3 = TP_FINAL  # 100% of the way

print(f"Current position: 3 ATOM SHORT @ ${ENTRY}")
print(f"\nProposed 3-tier TP system:")
print(f"  TP1: ${TP1} (1 contract) - {((ENTRY - TP1) / ENTRY * 100):.2f}% profit")
print(f"  TP2: ${TP2} (1 contract) - {((ENTRY - TP2) / ENTRY * 100):.2f}% profit")
print(f"  TP3: ${TP3} (1 contract) - {((ENTRY - TP3) / ENTRY * 100):.2f}% profit")

response = input("\nProceed to cancel existing TP and set 3-tier TPs? (yes/no): ")

if response.lower() == 'yes':
    # Cancel existing algo orders
    print("\n📋 Getting current algo orders...")
    algo_orders = client._request("GET", "/api/v1/trade/orders-algo-pending", {"instId": SYMBOL, "orderType": "trigger"})
    
    for order in algo_orders:
        algo_id = order.get('algoId')
        trigger_price = order.get('triggerPrice')
        print(f"  Canceling algo order {algo_id} (trigger: ${trigger_price})")
        cancel_response = client._request("POST", "/api/v1/trade/cancel-algo", {
            "algoId": algo_id,
            "instId": SYMBOL
        })
        print(f"  ✅ Canceled: {cancel_response}")
    
    # Set new 3-tier TPs
    print(f"\n💰 Setting TP1 at ${TP1} (1 contract)...")
    tp1_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",
        "orderType": "trigger",
        "size": "1",
        "orderPrice": "-1",
        "triggerPrice": str(TP1),
        "triggerPriceType": "mark",
        "reduceOnly": "true"
    }
    tp1_response = client._request("POST", "/api/v1/trade/order-algo", tp1_payload)
    print(f"✅ TP1 set: {tp1_response}")
    
    print(f"\n💰 Setting TP2 at ${TP2} (1 contract)...")
    tp2_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",
        "orderType": "trigger",
        "size": "1",
        "orderPrice": "-1",
        "triggerPrice": str(TP2),
        "triggerPriceType": "mark",
        "reduceOnly": "true"
    }
    tp2_response = client._request("POST", "/api/v1/trade/order-algo", tp2_payload)
    print(f"✅ TP2 set: {tp2_response}")
    
    print(f"\n💰 Setting TP3 at ${TP3} (1 contract)...")
    tp3_payload = {
        "instId": SYMBOL,
        "marginMode": "cross",
        "positionSide": "net",
        "side": "buy",
        "orderType": "trigger",
        "size": "1",
        "orderPrice": "-1",
        "triggerPrice": str(TP3),
        "triggerPriceType": "mark",
        "reduceOnly": "true"
    }
    tp3_response = client._request("POST", "/api/v1/trade/order-algo", tp3_payload)
    print(f"✅ TP3 set: {tp3_response}")
    
    print("\n✅ 3-tier TP system configured!")
else:
    print("\n❌ Canceled by user")
