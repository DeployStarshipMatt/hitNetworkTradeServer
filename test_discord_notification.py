"""
Test Discord notification with all trade details.
Sends a test notification to verify all TP levels are shown.
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DISCORD_NOTIFICATION_WEBHOOK = os.getenv('DISCORD_NOTIFICATION_WEBHOOK')

def send_test_notification():
    """Send test trade notification with all details."""
    
    if not DISCORD_NOTIFICATION_WEBHOOK:
        print("❌ DISCORD_NOTIFICATION_WEBHOOK not set in .env")
        return False
    
    # Test trade data with all TP levels
    symbol = "BTC-USDT"
    side = "long"
    entry_price = 98500.0
    stop_loss = 96000.0
    take_profit = 102000.0
    take_profit_2 = 105000.0
    take_profit_3 = 108000.0
    position_size = 0.05
    leverage = 20
    order_id = "TEST-12345"
    position_value = position_size * entry_price
    risk_percent = 1.0
    risk_amount = 50.0  # Example: 1% of $5000 equity
    
    # Calculate profit dollars at each TP (position split equally)
    num_tps = 3
    size_per_tp = position_size / num_tps
    
    tp1_profit = (take_profit - entry_price) * size_per_tp
    tp2_profit = (take_profit_2 - entry_price) * size_per_tp
    tp3_profit = (take_profit_3 - entry_price) * size_per_tp
    
    # Determine emoji based on side
    side_emoji = "📈" if side.lower() in ["long", "buy"] else "📉"
    
    # Build notification embed
    embed = {
        "title": f"{side_emoji} Trade Executed: {symbol}",
        "color": 3066993 if side.lower() in ["long", "buy"] else 15158332,  # Green for long, red for short
        "fields": [
            {"name": "Side", "value": side.upper(), "inline": True},
            {"name": "Entry Price", "value": f"${entry_price:.2f}", "inline": True},
            {"name": "Leverage", "value": f"{leverage}x", "inline": True},
            {"name": "Size", "value": f"{position_size:.4f} contracts", "inline": True},
            {"name": "Position Value", "value": f"${position_value:.2f}", "inline": True},
            {"name": "⚠️ Risk", "value": f"{risk_percent}% (${risk_amount:.2f})", "inline": True},
            {"name": "🛑 Stop Loss", "value": f"${stop_loss:.2f}", "inline": True},
            {"name": "🎯 TP1", "value": f"${take_profit:.2f} (+${tp1_profit:.2f})", "inline": True},
            {"name": "🎯 TP2", "value": f"${take_profit_2:.2f} (+${tp2_profit:.2f})", "inline": True},
            {"name": "🎯 TP3", "value": f"${take_profit_3:.2f} (+${tp3_profit:.2f})", "inline": True},
        ],
        "footer": {"text": f"Order ID: {order_id}"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send webhook
    payload = {
        "embeds": [embed],
        "username": "Trading Bot",
        "content": "**🔔 NEW TRADE ALERT** (Test Notification)"
    }
    
    try:
        print("📤 Sending test notification to Discord...")
        print(f"   Webhook: {DISCORD_NOTIFICATION_WEBHOOK[:50]}...")
        
        response = requests.post(DISCORD_NOTIFICATION_WEBHOOK, json=payload, timeout=10)
        
        if response.status_code == 204:
            print("✅ Test notification sent successfully!")
            print("\n📊 Notification Details:")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side.upper()}")
            print(f"   Entry: ${entry_price:,.2f}")
            print(f"   Stop Loss: ${stop_loss:,.2f}")
            print(f"   Risk: {risk_percent}% (${risk_amount:.2f})")
            print(f"\n   Position Split: {size_per_tp:.4f} contracts per TP")
            print(f"   TP1: ${take_profit:,.2f} (+${tp1_profit:.2f} profit)")
            print(f"   TP2: ${take_profit_2:,.2f} (+${tp2_profit:.2f} profit)")
            print(f"   TP3: ${take_profit_3:,.2f} (+${tp3_profit:.2f} profit)")
            print(f"   Total Potential Profit: ${tp1_profit + tp2_profit + tp3_profit:.2f}")
            print(f"\n   Leverage: {leverage}x")
            print(f"   Position Size: {position_size} contracts")
            print(f"   Position Value: ${position_value:,.2f}")
            print(f"   Order ID: {order_id}")
            print("\n✅ Check your Discord channel for the notification!")
            return True
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False


def send_error_notification_test():
    """Test error notification format."""
    
    if not DISCORD_NOTIFICATION_WEBHOOK:
        print("❌ DISCORD_NOTIFICATION_WEBHOOK not set in .env")
        return False
    
    symbol = "INVALID-USDT"
    side = "long"
    error_message = "Exchange does not support INVALID-USDT. This is a test error notification."
    
    embed = {
        "title": f"⚠️ Trade Rejected: {symbol}",
        "description": error_message,
        "color": 15844367,  # Yellow/orange for warning
        "fields": [
            {"name": "Symbol", "value": symbol, "inline": True},
            {"name": "Side", "value": side.upper(), "inline": True},
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "BloFin Trading Bot"}
    }
    
    payload = {
        "embeds": [embed],
        "username": "Trading Bot"
    }
    
    try:
        print("\n📤 Sending test error notification to Discord...")
        response = requests.post(DISCORD_NOTIFICATION_WEBHOOK, json=payload, timeout=10)
        
        if response.status_code == 204:
            print("✅ Test error notification sent successfully!")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("DISCORD NOTIFICATION TEST")
    print("=" * 70)
    print("\nThis will send test notifications to your Discord channel.")
    print("Make sure your webhook URL is configured in .env\n")
    
    # Test successful trade notification
    success1 = send_test_notification()
    
    # Test error notification
    success2 = send_error_notification_test()
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("✅ ALL TESTS PASSED")
        print("\nYour Discord notifications are working!")
        print("They will trigger immediately when trades execute.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check your DISCORD_NOTIFICATION_WEBHOOK in .env")
    print("=" * 70)
