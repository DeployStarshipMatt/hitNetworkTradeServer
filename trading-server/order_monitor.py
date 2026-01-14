"""
Order Monitor Module

Tracks TP/SL orders and sends Discord notifications when they fill.
Runs every 30 seconds to check order status.
"""
import logging
import time
from typing import Dict, Set, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class OrderMonitor:
    """Monitors TP/SL orders and sends Discord notifications when filled."""
    
    def __init__(self, blofin_client, webhook_url: Optional[str] = None, check_interval: int = 30):
        """
        Initialize order monitor.
        
        Args:
            blofin_client: BloFinClient instance
            webhook_url: Discord webhook URL
            check_interval: Check interval in seconds (default 30)
        """
        self.client = blofin_client
        self.webhook_url = webhook_url
        self.check_interval = check_interval
        
        # Track orders we're monitoring
        # Key: orderId, Value: order details
        self.tracked_orders: Dict[str, Dict] = {}
        
        # Track orders we've already notified about
        self.notified_orders: Set[str] = set()
        
        logger.info(f"📡 Order Monitor initialized (check interval: {check_interval}s)")
    
    def track_order(self, symbol: str, order_id: str, order_type: str, 
                   trigger_price: float, size: float, side: str,
                   entry_price: Optional[float] = None):
        """
        Start tracking a TP/SL order.
        
        Args:
            symbol: Trading pair
            order_id: Algo order ID
            order_type: 'TP1', 'TP2', 'TP3', or 'SL'
            trigger_price: Trigger price
            size: Order size
            side: Order side
            entry_price: Entry price for profit calculation
        """
        self.tracked_orders[order_id] = {
            'symbol': symbol,
            'type': order_type,
            'trigger_price': trigger_price,
            'size': size,
            'side': side,
            'entry_price': entry_price,
            'tracked_since': datetime.utcnow().isoformat()
        }
        logger.info(f"📍 Tracking {order_type} order: {symbol} {order_id} @ ${trigger_price}")
    
    def check_orders(self):
        """
        Check all tracked orders for fills.
        Called every 30 seconds by background worker.
        """
        if not self.tracked_orders:
            return
        
        try:
            # Get all pending TP/SL orders from exchange
            pending_orders = self.client._request(
                "GET",
                "/api/v1/copytrading/trade/pending-tpsl-by-order"
            )
            
            # Build set of pending order IDs
            pending_ids = set()
            if isinstance(pending_orders, list):
                pending_ids = {order.get('algoId') for order in pending_orders if order.get('algoId')}
            elif isinstance(pending_orders, dict) and 'data' in pending_orders:
                pending_ids = {order.get('algoId') for order in pending_orders['data'] if order.get('algoId')}
            
            # Check each tracked order
            for order_id, order_info in list(self.tracked_orders.items()):
                # If order is no longer pending, it must have filled
                if order_id not in pending_ids and order_id not in self.notified_orders:
                    self._handle_filled_order(order_id, order_info)
                    self.notified_orders.add(order_id)
                    del self.tracked_orders[order_id]
        
        except Exception as e:
            logger.error(f"Error checking orders: {e}")
    
    def _handle_filled_order(self, order_id: str, order_info: Dict):
        """
        Handle a filled order - send Discord notification.
        
        Args:
            order_id: Order ID that filled
            order_info: Order details
        """
        order_type = order_info['type']
        symbol = order_info['symbol']
        trigger_price = order_info['trigger_price']
        size = order_info['size']
        side = order_info['side']
        entry_price = order_info.get('entry_price')
        
        # Determine if this was TP or SL
        is_tp = order_type.startswith('TP')
        is_sl = order_type == 'SL'
        
        # Calculate profit/loss
        pnl = 0
        if entry_price:
            if side.lower() == 'sell':  # Closing long
                pnl = (trigger_price - entry_price) * size
            else:  # Closing short (side = buy)
                pnl = (entry_price - trigger_price) * size
        
        logger.info(f"{'✅' if is_tp else '❌'} {order_type} HIT: {symbol} @ ${trigger_price} "
                   f"({'+' if pnl > 0 else ''}${pnl:.2f})")
        
        # Send Discord notification
        self._send_notification(
            symbol=symbol,
            order_type=order_type,
            trigger_price=trigger_price,
            size=size,
            pnl=pnl,
            is_tp=is_tp
        )
    
    def _send_notification(self, symbol: str, order_type: str, trigger_price: float,
                          size: float, pnl: float, is_tp: bool):
        """
        Send Discord webhook notification.
        
        Args:
            symbol: Trading pair
            order_type: 'TP1', 'TP2', 'TP3', or 'SL'
            trigger_price: Price where order filled
            size: Order size
            pnl: Profit/loss in dollars
            is_tp: True if take profit, False if stop loss
        """
        if not self.webhook_url:
            return
        
        try:
            # Build embed
            if is_tp:
                title = f"✅ {order_type} Hit: {symbol}"
                color = 5763719  # Green
                pnl_text = f"+${pnl:.2f}"
            else:
                title = f"❌ Stop Loss Hit: {symbol}"
                color = 15158332  # Red
                pnl_text = f"-${abs(pnl):.2f}"
            
            embed = {
                "title": title,
                "color": color,
                "fields": [
                    {"name": "Price", "value": f"${trigger_price:.2f}", "inline": True},
                    {"name": "Size", "value": f"{size:.4f} contracts", "inline": True},
                    {"name": "Profit/Loss", "value": pnl_text, "inline": True},
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "BloFin Trading Bot"}
            }
            
            payload = {
                "embeds": [embed],
                "username": "Trading Bot"
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"📤 Discord notification sent: {order_type} filled")
            else:
                logger.warning(f"Failed to send Discord notification: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            'tracked_orders': len(self.tracked_orders),
            'notified_orders': len(self.notified_orders),
            'tracked_order_ids': list(self.tracked_orders.keys())
        }
