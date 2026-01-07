"""
Reusable Trade Executor Module

Handles complete trade execution with proper risk management:
- Calculates position size for 1% risk (ignores signal leverage)
- Places market order
- Sets stop loss and take profit
- Validates all parameters before execution
"""

import logging
from typing import Dict, Any, Optional
from blofin_client import BloFinClient

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Execute trades with proper risk management and validation"""
    
    def __init__(self, client: BloFinClient):
        """
        Initialize trade executor.
        
        Args:
            client: BloFinClient instance
        """
        self.client = client
        self.stats = {
            'trades_executed': 0,
            'trades_failed': 0,
            'total_risk': 0.0
        }
    
    def execute_trade(self, symbol: str, side: str, entry_price: float, 
                     stop_loss: float, take_profit: float, 
                     risk_percent: float = 1.0,
                     use_3tier_tp: bool = False) -> Dict[str, Any]:
        """
        Execute a complete trade with SL/TP.
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            side: "long" or "short"
            entry_price: Entry price (for calculation, market order executes at current)
            stop_loss: Stop loss price
            take_profit: Take profit price (or TP1 if using 3-tier)
            risk_percent: Percent of account to risk (default 1.0)
            use_3tier_tp: If True, assumes take_profit is TP1 and creates 3 levels
            
        Returns:
            Dict with execution results
        """
        logger.info(f"=" * 60)
        logger.info(f"EXECUTING TRADE: {symbol} {side.upper()}")
        logger.info(f"=" * 60)
        
        try:
            # 1. Validate inputs
            self._validate_trade_params(symbol, side, entry_price, stop_loss, take_profit)
            
            # 2. Calculate position size for 1% risk
            size_info = self.client.calculate_position_size(
                symbol=symbol,
                entry_price=entry_price,
                stop_loss=stop_loss,
                risk_percent=risk_percent
            )
            
            logger.info(f"Position Sizing:")
            logger.info(f"  Available Balance: ${size_info['available_balance']:.2f}")
            logger.info(f"  Risk Amount: ${size_info['risk_amount']:.4f} ({risk_percent}%)")
            logger.info(f"  Position Size: {size_info['size']} (from {size_info['raw_size']:.4f})")
            logger.info(f"  Notional Value: ${size_info['notional_value']:.2f}")
            logger.info(f"  Margin Needed: ${size_info['margin_needed']:.2f} @ {size_info['leverage']}x")
            
            # 3. Place market order
            order_side = "buy" if side.lower() == "long" else "sell"
            logger.info(f"\nPlacing market order: {order_side.upper()} {size_info['size']} {symbol}...")
            
            order_result = self.client.place_market_order(
                symbol=symbol,
                side=order_side,
                size=size_info['size']
            )
            
            if not order_result or not order_result.get('order_id'):
                raise Exception(f"Order failed: {order_result}")
            
            logger.info(f"✅ Order placed: {order_result['order_id']}")
            
            # 4. Set stop loss (opposite side of entry)
            sl_side = "sell" if side.lower() == "long" else "buy"
            logger.info(f"\nSetting stop loss: {sl_side.upper()} @ ${stop_loss}...")
            
            sl_result = self.client.set_stop_loss(
                symbol=symbol,
                side=sl_side,
                trigger_price=stop_loss,
                size=size_info['size']
            )
            
            logger.info(f"✅ Stop loss set: {sl_result['order_id']}")
            
            # 5. Set take profit
            tp_side = sl_side  # Same as SL (opposite of entry)
            
            if use_3tier_tp:
                logger.info(f"\nSetting 3-tier take profit...")
                tp_results = self._set_3tier_tp(
                    symbol=symbol,
                    side=tp_side,
                    size=size_info['size'],
                    tp1=take_profit,
                    entry=entry_price
                )
                logger.info(f"✅ 3-tier TP set: {tp_results}")
            else:
                logger.info(f"\nSetting take profit: {tp_side.upper()} @ ${take_profit}...")
                tp_result = self.client.set_take_profit(
                    symbol=symbol,
                    side=tp_side,
                    trigger_price=take_profit,
                    size=size_info['size']
                )
                logger.info(f"✅ Take profit set: {tp_result['order_id']}")
                tp_results = [tp_result]
            
            # 6. Summary
            self.stats['trades_executed'] += 1
            self.stats['total_risk'] += size_info['risk_amount']
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"TRADE EXECUTION COMPLETE")
            logger.info(f"{'=' * 60}")
            
            return {
                'success': True,
                'symbol': symbol,
                'side': side,
                'order': order_result,
                'stop_loss': sl_result,
                'take_profit': tp_results,
                'size_info': size_info
            }
            
        except Exception as e:
            self.stats['trades_failed'] += 1
            logger.error(f"❌ Trade execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_trade_params(self, symbol: str, side: str, entry: float, 
                               stop_loss: float, take_profit: float) -> None:
        """Validate trade parameters"""
        if side.lower() not in ['long', 'short']:
            raise ValueError(f"Invalid side: {side}. Must be 'long' or 'short'")
        
        if entry <= 0 or stop_loss <= 0 or take_profit <= 0:
            raise ValueError("Prices must be positive")
        
        # Validate SL/TP logic
        if side.lower() == 'long':
            if stop_loss >= entry:
                raise ValueError(f"LONG: Stop loss ({stop_loss}) must be below entry ({entry})")
            if take_profit <= entry:
                raise ValueError(f"LONG: Take profit ({take_profit}) must be above entry ({entry})")
        else:  # short
            if stop_loss <= entry:
                raise ValueError(f"SHORT: Stop loss ({stop_loss}) must be above entry ({entry})")
            if take_profit >= entry:
                raise ValueError(f"SHORT: Take profit ({take_profit}) must be below entry ({entry})")
    
    def _set_3tier_tp(self, symbol: str, side: str, size: float, 
                      tp1: float, entry: float) -> list:
        """Set 3-tier take profit levels"""
        # Split position into 3 parts
        tp_size = size // 3
        remaining = size - (tp_size * 2)
        
        # Calculate TP levels (TP2 and TP3 based on TP1 distance)
        tp_distance = abs(tp1 - entry)
        direction = 1 if entry > tp1 else -1  # -1 for short, +1 for long
        
        tp2 = entry - (direction * tp_distance * 2)
        tp3 = entry - (direction * tp_distance * 3)
        
        logger.info(f"  TP1: {tp_size} @ ${tp1:.6f}")
        logger.info(f"  TP2: {tp_size} @ ${tp2:.6f}")
        logger.info(f"  TP3: {remaining} @ ${tp3:.6f}")
        
        results = []
        
        # TP1
        tp1_result = self.client.set_take_profit(symbol, side, tp1, tp_size)
        results.append(tp1_result)
        logger.info(f"  ✅ TP1: {tp1_result['order_id']}")
        
        # TP2
        tp2_result = self.client.set_take_profit(symbol, side, tp2, tp_size)
        results.append(tp2_result)
        logger.info(f"  ✅ TP2: {tp2_result['order_id']}")
        
        # TP3
        tp3_result = self.client.set_take_profit(symbol, side, tp3, remaining)
        results.append(tp3_result)
        logger.info(f"  ✅ TP3: {tp3_result['order_id']}")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return self.stats.copy()
