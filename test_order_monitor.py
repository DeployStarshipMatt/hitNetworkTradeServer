"""
Test Order Monitoring System

Simulates the order monitoring workflow to verify notifications work.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "trading-server"))

from order_monitor import OrderMonitor
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 70)
print("ORDER MONITORING TEST")
print("=" * 70)

# Create a mock BloFin client for testing
class MockBloFinClient:
    def __init__(self):
        self.pending_orders = [
            {'algoId': 'TP1-12345', 'status': 'pending'},
            {'algoId': 'TP2-12345', 'status': 'pending'},
            {'algoId': 'SL-12345', 'status': 'pending'}
        ]
    
    def _request(self, method, path, body=None):
        # Simulate API response - return pending orders
        return self.pending_orders

# Initialize monitor with test client
webhook_url = os.getenv('DISCORD_NOTIFICATION_WEBHOOK')
mock_client = MockBloFinClient()

monitor = OrderMonitor(
    blofin_client=mock_client,
    webhook_url=webhook_url,
    check_interval=30
)

print("\n📍 Tracking Test Orders:")
print("-" * 70)

# Track some orders
monitor.track_order(
    symbol='BTC-USDT',
    order_id='TP1-12345',
    order_type='TP1',
    trigger_price=102000.0,
    size=0.0167,
    side='sell',
    entry_price=98500.0
)

monitor.track_order(
    symbol='BTC-USDT',
    order_id='TP2-12345',
    order_type='TP2',
    trigger_price=105000.0,
    size=0.0167,
    side='sell',
    entry_price=98500.0
)

monitor.track_order(
    symbol='BTC-USDT',
    order_id='SL-12345',
    order_type='SL',
    trigger_price=96000.0,
    size=0.05,
    side='sell',
    entry_price=98500.0
)

# Show stats
stats = monitor.get_stats()
print(f"\nMonitor Stats:")
print(f"  Tracked Orders: {stats['tracked_orders']}")
print(f"  Order IDs: {stats['tracked_order_ids']}")

# Simulate first check - all orders still pending
print("\n🔍 Check #1: All orders still pending...")
monitor.check_orders()
stats = monitor.get_stats()
print(f"  Tracked: {stats['tracked_orders']}, Notified: {stats['notified_orders']}")

# Simulate TP1 filled (remove from pending list)
print("\n🎯 Simulating TP1 filled...")
mock_client.pending_orders = [
    {'algoId': 'TP2-12345', 'status': 'pending'},
    {'algoId': 'SL-12345', 'status': 'pending'}
]

print("🔍 Check #2: Detecting filled orders...")
monitor.check_orders()
stats = monitor.get_stats()
print(f"  Tracked: {stats['tracked_orders']}, Notified: {stats['notified_orders']}")

# Simulate TP2 filled
print("\n🎯 Simulating TP2 filled...")
mock_client.pending_orders = [
    {'algoId': 'SL-12345', 'status': 'pending'}
]

print("🔍 Check #3: Detecting more fills...")
monitor.check_orders()
stats = monitor.get_stats()
print(f"  Tracked: {stats['tracked_orders']}, Notified: {stats['notified_orders']}")

# Simulate SL filled (loss scenario)
print("\n❌ Simulating Stop Loss filled...")
mock_client.pending_orders = []

print("🔍 Check #4: Final check...")
monitor.check_orders()
stats = monitor.get_stats()
print(f"  Tracked: {stats['tracked_orders']}, Notified: {stats['notified_orders']}")

print("\n" + "=" * 70)
print("✅ ORDER MONITORING TEST COMPLETE")
print("=" * 70)
print("\nCheck your Discord channel for notifications!")
print("\nExpected notifications:")
print("  1. ✅ TP1 Hit: BTC-USDT @ $102,000 (+$58.33)")
print("  2. ✅ TP2 Hit: BTC-USDT @ $105,000 (+$108.33)")
print("  3. ❌ Stop Loss Hit: BTC-USDT @ $96,000 (-$125.00)")
print("=" * 70)
