"""
Manual trade execution script
"""
import os
import sys
from dotenv import load_dotenv

# Add trading-server to path
sys.path.append('trading-server')
sys.path.append('shared')

from blofin_client import BloFinClient
from blofin_auth import BloFinAuth

# Load environment
load_dotenv('trading-server/.env')

# Trade parameters from signal
SYMBOL = "CFX-USDT"
SIDE = "short"
ENTRY_PRICE = 0.080102
STOP_LOSS = 0.081832
TAKE_PROFIT = 0.079653  # TP1
LEVERAGE = 23

# Risk management
RISK_PERCENT = 1.0  # 1% risk per trade
MAX_POSITION_VALUE = 100  # Max $100 position to avoid size errors

def execute_trade():
    # Initialize BloFin client
    base_url = os.getenv('BLOFIN_BASE_URL')
    api_key = os.getenv('BLOFIN_API_KEY')
    secret_key = os.getenv('BLOFIN_SECRET_KEY')
    passphrase = os.getenv('BLOFIN_PASSPHRASE')
    
    client = BloFinClient(api_key, secret_key, passphrase, base_url)
    
    print(f"🎯 Executing CFX/USDT SHORT trade")
    print(f"Entry: {ENTRY_PRICE}")
    print(f"Stop Loss: {STOP_LOSS}")
    print(f"Take Profit: {TAKE_PROFIT}")
    print(f"Leverage: {LEVERAGE}x")
    print()
    
    # Get account balance
    balance_result = client.get_account_balance()
    print(f"Balance result: {balance_result}")
    
    available_balance = float(balance_result['details'][0]['available'])
    print(f"💰 Available Balance: ${available_balance:.2f} USDT")
    
    # Calculate position size based on risk
    risk_amount = available_balance * (RISK_PERCENT / 100)
    sl_distance_percent = abs((STOP_LOSS - ENTRY_PRICE) / ENTRY_PRICE) * 100
    
    # Position size = Risk / (Entry × SL Distance %)
    position_size = risk_amount / (ENTRY_PRICE * (sl_distance_percent / 100))
    
    # Cap position value to avoid size errors
    position_value = position_size * ENTRY_PRICE
    if position_value > MAX_POSITION_VALUE:
        position_size = MAX_POSITION_VALUE / ENTRY_PRICE
        position_value = MAX_POSITION_VALUE
    
    # Round position size to 2 decimal places
    # For testing, use smaller amount
    position_size = 10.0  # Start with 10 CFX for testing
    position_value = position_size * ENTRY_PRICE
    
    # Calculate required leverage
    required_leverage = position_value / available_balance
    
    # Use specified leverage (capped at 20x max)
    actual_leverage = min(max(int(required_leverage), 2), 20)
    
    print(f"📊 Risk: ${risk_amount:.2f} ({RISK_PERCENT}%)")
    print(f"📏 SL Distance: {sl_distance_percent:.2f}%")
    print(f"📦 Position Size: {position_size:.4f} CFX")
    print(f"⚖️ Leverage: {actual_leverage}x")
    print()
    
    # Set leverage
    print(f"⚙️ Setting leverage to {actual_leverage}x...")
    leverage_result = client.set_leverage(
        symbol=SYMBOL,
        leverage=str(actual_leverage),
        margin_mode="cross"
    )
    print(f"Leverage result: {leverage_result}")
    print()
    
    # Place limit order at entry price
    print(f"📤 Placing SHORT limit order...")
    order_result = client.place_limit_order(
        symbol=SYMBOL,
        side=SIDE,
        size=position_size,
        price=ENTRY_PRICE,
        trade_mode="cross"
    )
    
    print(f"✅ Order placed: {order_result}")
    order_id = order_result.get('order_id')
    print()
    
    # Set stop loss
    if order_id and STOP_LOSS:
        print(f"🛡️ Setting stop loss at {STOP_LOSS}...")
        try:
            sl_result = client.set_stop_loss(
                symbol=SYMBOL,
                side="buy",  # Opposite side for SHORT
                size=position_size,
                trigger_price=STOP_LOSS,
                trade_mode="cross"
            )
            print(f"✅ Stop loss set: {sl_result}")
        except Exception as e:
            print(f"⚠️ Failed to set stop loss: {e}")
    
    # Set take profit
    if order_id and TAKE_PROFIT:
        print(f"💰 Setting take profit at {TAKE_PROFIT}...")
        try:
            tp_result = client.set_take_profit(
                symbol=SYMBOL,
                side="buy",  # Opposite side for SHORT
                size=position_size,
                trigger_price=TAKE_PROFIT,
                trade_mode="cross"
            )
            print(f"✅ Take profit set: {tp_result}")
        except Exception as e:
            print(f"⚠️ Failed to set take profit: {e}")
    
    print()
    print("🎉 Trade execution complete!")

if __name__ == "__main__":
    execute_trade()
