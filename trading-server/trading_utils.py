"""
Trading Utilities Module

Reusable functions for managing positions, orders, and algo orders.
Eliminates need for creating individual scripts for common tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from blofin_client import BloFinClient

logger = logging.getLogger(__name__)


def get_all_positions(client: BloFinClient) -> List[Dict[str, Any]]:
    """
    Get all open positions.
    
    Returns:
        List of position dictionaries
    """
    return client.get_positions()


def get_position(client: BloFinClient, symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get specific position by symbol.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair (e.g., "BTC-USDT")
        
    Returns:
        Position dict or None if not found
    """
    positions = client.get_positions()
    for pos in positions:
        if pos['instId'] == symbol:
            return pos
    return None


def print_position_summary(client: BloFinClient, symbol: Optional[str] = None) -> None:
    """
    Print formatted position summary.
    
    Args:
        client: BloFinClient instance
        symbol: Optional specific symbol, otherwise prints all
    """
    positions = client.get_positions()
    
    if symbol:
        positions = [p for p in positions if p['instId'] == symbol]
    
    if not positions:
        print("No open positions")
        return
    
    print("=" * 70)
    print("OPEN POSITIONS")
    print("=" * 70)
    
    for p in positions:
        side = "LONG" if float(p['positions']) > 0 else "SHORT"
        print(f"\n{p['instId']} {side}:")
        print(f"  Size: {p['positions']}")
        print(f"  Entry: ${p['averagePrice']}")
        print(f"  Current: ${p['markPrice']}")
        print(f"  PnL: ${p['unrealizedPnl']} ({float(p['unrealizedPnlRatio'])*100:.2f}%)")
        print(f"  Leverage: {p['leverage']}x")
        print(f"  Margin: ${p['initialMargin']}")


def get_algo_orders(client: BloFinClient, symbol: str) -> List[Dict[str, Any]]:
    """
    Get all pending algo orders for a symbol.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        
    Returns:
        List of algo order dictionaries
    """
    try:
        response = client._request("GET", "/api/v1/trade/orders-algo-pending", {
            "instId": symbol,
            "orderType": "trigger"
        })
        return response if response else []
    except Exception as e:
        logger.error(f"Error getting algo orders for {symbol}: {e}")
        return []


def print_algo_orders(client: BloFinClient, symbol: str) -> None:
    """
    Print formatted algo orders (SL/TP) for a symbol.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
    """
    orders = get_algo_orders(client, symbol)
    
    if not orders:
        print(f"No algo orders for {symbol}")
        return
    
    print(f"\n{symbol} Algo Orders:")
    print("-" * 50)
    
    # Get position to determine SL vs TP
    position = get_position(client, symbol)
    entry = float(position['averagePrice']) if position else 0
    
    for order in orders:
        trigger = float(order['triggerPrice'])
        size = order['size']
        algo_id = order['algoId']
        
        # Determine if SL or TP based on trigger price vs entry
        if position:
            pos_size = float(position['positions'])
            if pos_size > 0:  # LONG
                order_type = "STOP LOSS" if trigger < entry else "TAKE PROFIT"
            else:  # SHORT
                order_type = "STOP LOSS" if trigger > entry else "TAKE PROFIT"
        else:
            order_type = "ALGO ORDER"
        
        print(f"  {order_type}: ${trigger:.6f} ({size} units) - ID: {algo_id}")


def cancel_algo_order(client: BloFinClient, symbol: str, algo_id: str) -> bool:
    """
    Cancel a specific algo order.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        algo_id: Algo order ID to cancel
        
    Returns:
        True if successful
    """
    try:
        result = client._request("POST", "/api/v1/trade/cancel-algo", {
            "instId": symbol,
            "algoId": algo_id
        })
        return result.get('code') == '0'
    except Exception as e:
        logger.error(f"Error canceling algo order {algo_id}: {e}")
        return False


def cancel_all_algo_orders(client: BloFinClient, symbol: str) -> int:
    """
    Cancel all algo orders for a symbol.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        
    Returns:
        Number of orders canceled
    """
    orders = get_algo_orders(client, symbol)
    canceled = 0
    
    for order in orders:
        if cancel_algo_order(client, symbol, order['algoId']):
            canceled += 1
            logger.info(f"Canceled {order['algoId']}")
    
    return canceled


def set_position_protection(client: BloFinClient, symbol: str, stop_loss: float, 
                           take_profit: float, tp2: Optional[float] = None, 
                           tp3: Optional[float] = None) -> Dict[str, Any]:
    """
    Set stop loss and take profit(s) on an existing position.
    Automatically determines side based on position direction.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        stop_loss: Stop loss price
        take_profit: Take profit price (TP1 if multiple TPs)
        tp2: Optional second take profit
        tp3: Optional third take profit
        
    Returns:
        Dict with results
    """
    # Get position
    position = get_position(client, symbol)
    if not position:
        raise ValueError(f"No position found for {symbol}")
    
    pos_size = float(position['positions'])
    abs_size = abs(pos_size)
    
    # Determine close side (opposite of position)
    close_side = "sell" if pos_size > 0 else "buy"
    
    results = {}
    
    # Set stop loss for full position
    try:
        sl_result = client.set_stop_loss(symbol, close_side, stop_loss, abs_size)
        results['stop_loss'] = sl_result
        logger.info(f"Stop loss set: {sl_result['order_id']}")
    except Exception as e:
        logger.error(f"Failed to set stop loss: {e}")
        results['stop_loss'] = {'error': str(e)}
    
    # Set take profits
    if tp2 and tp3:
        # 3-tier TP
        tp_size = abs_size // 3
        remaining = abs_size - (tp_size * 2)
        
        try:
            tp1_result = client.set_take_profit(symbol, close_side, take_profit, tp_size)
            results['tp1'] = tp1_result
            logger.info(f"TP1 set: {tp1_result['order_id']}")
        except Exception as e:
            logger.error(f"Failed to set TP1: {e}")
            results['tp1'] = {'error': str(e)}
        
        try:
            tp2_result = client.set_take_profit(symbol, close_side, tp2, tp_size)
            results['tp2'] = tp2_result
            logger.info(f"TP2 set: {tp2_result['order_id']}")
        except Exception as e:
            logger.error(f"Failed to set TP2: {e}")
            results['tp2'] = {'error': str(e)}
        
        try:
            tp3_result = client.set_take_profit(symbol, close_side, tp3, remaining)
            results['tp3'] = tp3_result
            logger.info(f"TP3 set: {tp3_result['order_id']}")
        except Exception as e:
            logger.error(f"Failed to set TP3: {e}")
            results['tp3'] = {'error': str(e)}
    else:
        # Single TP
        try:
            tp_result = client.set_take_profit(symbol, close_side, take_profit, abs_size)
            results['take_profit'] = tp_result
            logger.info(f"Take profit set: {tp_result['order_id']}")
        except Exception as e:
            logger.error(f"Failed to set take profit: {e}")
            results['take_profit'] = {'error': str(e)}
    
    return results


def close_position(client: BloFinClient, symbol: str) -> Dict[str, Any]:
    """
    Close an existing position completely.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        
    Returns:
        Order result
    """
    position = get_position(client, symbol)
    if not position:
        raise ValueError(f"No position found for {symbol}")
    
    pos_size = float(position['positions'])
    abs_size = abs(pos_size)
    
    # Determine close side (opposite of position)
    close_side = "sell" if pos_size > 0 else "buy"
    
    # Place market order to close
    result = client.place_market_order(symbol, close_side, abs_size)
    logger.info(f"Closed {symbol} position: {abs_size} @ {close_side}")
    
    return result


def fix_position_protection(client: BloFinClient, symbol: str, stop_loss: float,
                           tp1: float, tp2: Optional[float] = None, 
                           tp3: Optional[float] = None) -> None:
    """
    Clean up and reset all SL/TP for a position.
    Cancels all existing algo orders and sets new ones.
    
    Args:
        client: BloFinClient instance
        symbol: Trading pair
        stop_loss: Stop loss price
        tp1: First take profit
        tp2: Optional second take profit
        tp3: Optional third take profit
    """
    print(f"\nFixing protection for {symbol}...")
    
    # Cancel all existing algo orders
    canceled = cancel_all_algo_orders(client, symbol)
    print(f"  Canceled {canceled} existing algo orders")
    
    # Set new protection
    results = set_position_protection(client, symbol, stop_loss, tp1, tp2, tp3)
    
    print(f"  Stop Loss: {results.get('stop_loss', {}).get('order_id', 'FAILED')}")
    if 'tp1' in results:
        print(f"  TP1: {results.get('tp1', {}).get('order_id', 'FAILED')}")
        print(f"  TP2: {results.get('tp2', {}).get('order_id', 'FAILED')}")
        print(f"  TP3: {results.get('tp3', {}).get('order_id', 'FAILED')}")
    else:
        print(f"  Take Profit: {results.get('take_profit', {}).get('order_id', 'FAILED')}")
    
    print("  Done!")


def get_account_summary(client: BloFinClient) -> None:
    """
    Print complete account summary with all positions and protection.
    """
    # Get balance
    balance_data = client.get_account_balance()
    if balance_data and 'details' in balance_data:
        available = float(balance_data['details'][0].get('available', 0))
        equity = float(balance_data['details'][0].get('equity', 0))
        
        print("=" * 70)
        print("ACCOUNT SUMMARY")
        print("=" * 70)
        print(f"Available Balance: ${available:.2f}")
        print(f"Total Equity: ${equity:.2f}")
    
    # Get positions
    print_position_summary(client)
    
    # Get algo orders for each position
    positions = get_all_positions(client)
    for pos in positions:
        symbol = pos['instId']
        print_algo_orders(client, symbol)
    
    print("\n" + "=" * 70)
