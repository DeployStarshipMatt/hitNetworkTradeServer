"""
Execute ATOM/USDT SHORT trade manually
"""
import os
import sys
from dotenv import load_dotenv

# Add trading-server to path
sys.path.append('trading-server')

from blofin_client import BloFinClient

# Load environment
load_dotenv('trading-server/.env')

# Trade parameters from signal
SYMBOL = "ATOM-USDT"
SIDE = "short"
ENTRY_PRICE = 2.413447
STOP_LOSS = 2.545951
TAKE_PROFIT = 2.354262  # TP1
LEVERAGE = 16

# Risk management
RISK_PERCENT = 1.0  # 1% risk per trade

def execute_trade():
    # Initialize BloFin client
    base_url = os.getenv('BLOFIN_BASE_URL')
    api_key = os.getenv('BLOFIN_API_KEY')
    secret_key = os.getenv('BLOFIN_SECRET_KEY')
    passphrase = os.getenv('BLOFIN_PASSPHRASE')
    
    client = BloFinClient(api_key, secret_key, passphrase, base_url)
    
    print(f"🎯 Executing ATOM/USDT SHORT trade")
    print(f"Entry: {ENTRY_PRICE}")
    print(f"Stop Loss: {STOP_LOSS}")
    print(f"Take Profit: {TAKE_PROFIT}")
    print(f"Leverage: {LEVERAGE}x")
    print()
    
    # Get account balance
    balance_result = client.get_account_balance()
    available_balance = float(balance_result['details'][0]['available'])
    print(f"💰 Available Balance: ${available_balance:.2f} USDT")
    
    # Calculate position size based on risk
    risk_amount = available_balance * (RISK_PERCENT / 100)
    sl_distance_percent = abs((STOP_LOSS - ENTRY_PRICE) / ENTRY_PRICE)
    
    # Position size = Risk / (Entry × SL Distance %)
    position_size = risk_amount / (ENTRY_PRICE * sl_distance_percent)
    
    # ATOM requires integer contract size
    position_size = max(1, int(position_size))
    
    # Calculate position value
    position_value = position_size * ENTRY_PRICE
    
    # Calculate actual leverage needed
    required_leverage = position_value / available_balance
    actual_leverage = min(max(int(round(required_leverage)), 2), 20)
    
    print(f"📊 Risk: ${risk_amount:.2f} ({RISK_PERCENT}%)")
    print(f"📏 SL Distance: {sl_distance_percent*100:.2f}%")
    print(f"📦 Position Size: {position_size:.1f} ATOM")
    print(f"⚖️ Leverage: {actual_leverage}x")
    print(f"💵 Position Value: ${position_value:.2f}")
    print()
    
    # Set leverage
    print(f"⚙️ Setting leverage to {actual_leverage}x...")
    try:
        leverage_result = client.set_leverage(
            symbol=SYMBOL,
            leverage=actual_leverage,
            margin_mode="cross"
        )
        print(f"✅ Leverage set: {leverage_result}")
    except Exception as e:
        print(f"⚠️ Failed to set leverage: {e}")
    print()
    
    # Place market order to ensure execution
    print(f"📤 Placing SHORT market order...")
    try:
        order_result = client.place_market_order(
            symbol=SYMBOL,
            side=SIDE,
            size=position_size,
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
        
    except Exception as e:
        print(f"❌ Failed to place order: {e}")

if __name__ == "__main__":
    execute_trade()
