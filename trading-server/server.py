"""
Trading Server - Main Application

FastAPI server that receives trade signals and executes on BloFin.
Self-contained service with REST API.
"""
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent))

from blofin_client import BloFinClient
from shared.models import TradeSignal, TradeResponse, HealthCheck

# Load environment variables
load_dotenv()

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
API_KEY = os.getenv('API_KEY')

# BloFin Configuration
BLOFIN_API_KEY = os.getenv('BLOFIN_API_KEY')
BLOFIN_SECRET_KEY = os.getenv('BLOFIN_SECRET_KEY')
BLOFIN_PASSPHRASE = os.getenv('BLOFIN_PASSPHRASE')
BLOFIN_BASE_URL = os.getenv('BLOFIN_BASE_URL', 'https://demo-trading-openapi.blofin.com')

# Trading Configuration
DEFAULT_TRADE_MODE = os.getenv('DEFAULT_TRADE_MODE', 'cross')
DEFAULT_LEVERAGE = int(os.getenv('DEFAULT_LEVERAGE', 10))
MAX_LEVERAGE = int(os.getenv('MAX_LEVERAGE', 20))
MAX_POSITION_SIZE_USD = float(os.getenv('MAX_POSITION_SIZE_USD', 1000))
RISK_PER_TRADE_PERCENT = float(os.getenv('RISK_PER_TRADE_PERCENT', 1))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'trading_server.log')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trading Server",
    description="Receives trade signals and executes on BloFin",
    version="1.0.0"
)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from request."""
    if not API_KEY:
        logger.warning("API_KEY not configured - allowing all requests")
        return True
    
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


# Initialize BloFin client
blofin_client: Optional[BloFinClient] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global blofin_client
    
    logger.info("🚀 Starting Trading Server...")
    logger.info(f"📡 BloFin API: {BLOFIN_BASE_URL}")
    
    # Validate BloFin credentials
    if not all([BLOFIN_API_KEY, BLOFIN_SECRET_KEY, BLOFIN_PASSPHRASE]):
        logger.error("❌ BloFin credentials not configured!")
        logger.warning("⚠️ Server will start but trading will fail")
    else:
        try:
            blofin_client = BloFinClient(
                api_key=BLOFIN_API_KEY,
                secret_key=BLOFIN_SECRET_KEY,
                passphrase=BLOFIN_PASSPHRASE,
                base_url=BLOFIN_BASE_URL
            )
            logger.info("✅ BloFin client initialized")
            
            # Test connection (optional - comment out if causing issues)
            # balance = blofin_client.get_account_balance()
            # logger.info(f"✅ BloFin connection verified")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize BloFin client: {e}")
            blofin_client = None


def calculate_position_size_and_leverage(
    entry_price: float,
    stop_loss: Optional[float],
    available_balance: float,
    risk_percent: float,
    max_leverage: int
) -> tuple[float, int]:
    """
    Calculate optimal position size and leverage based on stop loss distance.
    
    Args:
        entry_price: Entry price for the trade
        stop_loss: Stop loss price (None if no SL)
        available_balance: Available account balance in USD
        risk_percent: Percentage of balance to risk (e.g., 1 for 1%)
        max_leverage: Maximum allowed leverage
        
    Returns:
        (position_size_in_contracts, leverage)
    """
    # Calculate risk amount in USD
    risk_amount = available_balance * (risk_percent / 100)
    
    # If no stop loss provided, use default conservative sizing
    if not stop_loss or stop_loss <= 0:
        logger.warning("⚠️ No stop loss provided, using conservative 2% position size")
        position_value = available_balance * 0.02  # 2% of balance
        position_size = position_value / entry_price
        leverage = max(1, min(5, int(position_value / available_balance)))  # Max 5x without SL
        return position_size, leverage
    
    # Calculate stop loss distance as percentage
    sl_distance_pct = abs(entry_price - stop_loss) / entry_price
    
    # Prevent division by zero
    if sl_distance_pct < 0.0001:  # Less than 0.01%
        logger.warning("⚠️ Stop loss too close to entry, using minimum distance")
        sl_distance_pct = 0.01  # 1% minimum
    
    # Calculate position size based on risk and SL distance
    # Risk = Position Size × Entry Price × SL Distance %
    # Therefore: Position Size = Risk / (Entry Price × SL Distance %)
    position_size = risk_amount / (entry_price * sl_distance_pct)
    
    # Calculate required leverage
    # Position Value = Position Size × Entry Price
    # Leverage = Position Value / Available Balance
    position_value = position_size * entry_price
    required_leverage = position_value / available_balance
    
    # Cap leverage at maximum
    if required_leverage > max_leverage:
        logger.warning(f"⚠️ Required leverage {required_leverage:.1f}x exceeds max {max_leverage}x, adjusting position")
        required_leverage = max_leverage
        position_size = (available_balance * required_leverage) / entry_price
    
    # Round leverage to integer, minimum 1x
    leverage = max(1, int(round(required_leverage)))
    
    logger.info(f"📊 Position Calc: Entry=${entry_price:.2f}, SL=${stop_loss:.2f}, Distance={sl_distance_pct*100:.2f}%, "
                f"Risk=${risk_amount:.2f}, Size={position_size:.4f}, Leverage={leverage}x, Value=${position_value:.2f}")
    
    return position_size, leverage


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Trading Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = "healthy"
    details = {}
    
    # Check BloFin client
    if not blofin_client:
        health_status = "degraded"
        details['blofin'] = "not_initialized"
    else:
        details['blofin'] = "connected"
        details['stats'] = blofin_client.get_stats()
    
    health = HealthCheck(
        service="trading-server",
        status=health_status,
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )
    
    return health.to_dict()


@app.post("/api/v1/trade")
async def execute_trade(
    signal: dict,
    authenticated: bool = Depends(verify_api_key)
) -> dict:
    """
    Execute trade signal.
    
    Args:
        signal: TradeSignal data
        authenticated: Authentication status
        
    Returns:
        TradeResponse
    """
    try:
        # Parse signal
        trade_signal = TradeSignal.from_dict(signal)
        logger.info(f"📊 Received signal: {trade_signal.symbol} {trade_signal.side}")
        
        # Validate signal
        is_valid, error = trade_signal.validate()
        if not is_valid:
            logger.warning(f"❌ Invalid signal: {error}")
            return TradeResponse(
                success=False,
                signal_id=trade_signal.signal_id,
                message=f"Invalid signal: {error}",
                status="rejected",
                error_code="VALIDATION_ERROR"
            ).to_dict()
        
        # Check if BloFin client is available
        if not blofin_client:
            logger.error("❌ BloFin client not initialized")
            return TradeResponse(
                success=False,
                signal_id=trade_signal.signal_id,
                message="Trading service unavailable",
                status="failed",
                error_code="SERVICE_UNAVAILABLE"
            ).to_dict()
        
        # Calculate position size based on account balance
        try:
            position_size = trade_signal.size
            leverage = DEFAULT_LEVERAGE
            
            if not position_size:
                # Get account balance
                balance_info = blofin_client.get_account_balance()
                
                # Extract available balance (USDT)
                available_balance = 0
                if balance_info and 'details' in balance_info:
                    for balance in balance_info['details']:
                        if balance.get('currency') == 'USDT':
                            available_balance = float(balance.get('available', 0))
                            break
                
                if available_balance > 0:
                    # Get entry price (use current market price if not specified)
                    entry_price = trade_signal.entry_price
                    if not entry_price:
                        # For market orders, we need to estimate - use a conservative approach
                        # In production, you'd fetch current market price
                        logger.warning("⚠️ No entry price for market order, using conservative sizing")
                        position_size = 0.01
                        leverage = DEFAULT_LEVERAGE
                    else:
                        # Calculate optimal position size and leverage based on SL distance
                        position_size, leverage = calculate_position_size_and_leverage(
                            entry_price=entry_price,
                            stop_loss=trade_signal.stop_loss,
                            available_balance=available_balance,
                            risk_percent=RISK_PER_TRADE_PERCENT,
                            max_leverage=MAX_LEVERAGE
                        )
                    
                    logger.info(f"💰 Balance: ${available_balance:.2f}, Risk: {RISK_PER_TRADE_PERCENT}%, "
                               f"Position: {position_size:.4f} contracts, Leverage: {leverage}x")
                else:
                    position_size = 0.01  # Minimum fallback
                    leverage = DEFAULT_LEVERAGE
                    logger.warning(f"⚠️ Could not get balance, using minimum size: {position_size}")
        
        except Exception as e:
            logger.warning(f"⚠️ Position sizing failed: {e}, using default 0.01")
            position_size = 0.01
            leverage = DEFAULT_LEVERAGE
        
        # Set leverage for this symbol
        try:
            blofin_client.set_leverage(
                symbol=trade_signal.symbol,
                leverage=leverage,
                margin_mode=DEFAULT_TRADE_MODE
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not set leverage, continuing with default: {e}")
        
        # Execute order
        try:
            # Determine order type
            if trade_signal.entry_price:
                # Limit order
                order_result = blofin_client.place_limit_order(
                    symbol=trade_signal.symbol,
                    side=trade_signal.side,
                    size=position_size,
                    price=trade_signal.entry_price,
                    trade_mode=DEFAULT_TRADE_MODE
                )
            else:
                # Market order
                order_result = blofin_client.place_market_order(
                    symbol=trade_signal.symbol,
                    side=trade_signal.side,
                    size=position_size,
                    trade_mode=DEFAULT_TRADE_MODE
                )
            
            order_id = order_result.get('order_id')
            
            # Set stop loss if provided
            if trade_signal.stop_loss:
                try:
                    # Determine opposite side for SL
                    sl_side = "sell" if trade_signal.side in ["long", "buy"] else "buy"
                    blofin_client.set_stop_loss(
                        symbol=trade_signal.symbol,
                        side=sl_side,
                        size=position_size,
                        trigger_price=trade_signal.stop_loss,
                        trade_mode=DEFAULT_TRADE_MODE
                    )
                    logger.info(f"✅ Stop loss set @ {trade_signal.stop_loss}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to set stop loss: {e}")
            
            # Set take profit if provided
            if trade_signal.take_profit:
                try:
                    # Determine opposite side for TP
                    tp_side = "sell" if trade_signal.side in ["long", "buy"] else "buy"
                    blofin_client.set_take_profit(
                        symbol=trade_signal.symbol,
                        side=tp_side,
                        size=position_size,
                        trigger_price=trade_signal.take_profit,
                        trade_mode=DEFAULT_TRADE_MODE
                    )
                    logger.info(f"✅ Take profit set @ {trade_signal.take_profit}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to set take profit: {e}")
            
            # Success response
            logger.info(f"✅ Trade executed: {order_id}")
            return TradeResponse(
                success=True,
                signal_id=trade_signal.signal_id,
                order_id=order_id,
                message="Trade executed successfully",
                status="executed",
                executed_at=datetime.utcnow().isoformat()
            ).to_dict()
        
        except Exception as e:
            logger.error(f"❌ Order execution failed: {e}")
            return TradeResponse(
                success=False,
                signal_id=trade_signal.signal_id,
                message=f"Order execution failed: {str(e)}",
                status="failed",
                error_code="EXECUTION_ERROR",
                error_details=str(e)
            ).to_dict()
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        return TradeResponse(
            success=False,
            message=f"Internal server error: {str(e)}",
            status="failed",
            error_code="INTERNAL_ERROR"
        ).to_dict()


@app.get("/api/v1/stats")
async def get_stats(authenticated: bool = Depends(verify_api_key)):
    """Get trading statistics."""
    if not blofin_client:
        return {"error": "BloFin client not initialized"}
    
    return blofin_client.get_stats()


@app.get("/api/v1/balance")
async def get_balance(authenticated: bool = Depends(verify_api_key)):
    """Get account balance."""
    if not blofin_client:
        raise HTTPException(status_code=503, detail="BloFin client not initialized")
    
    try:
        balance = blofin_client.get_account_balance()
        return balance
    except Exception as e:
        logger.error(f"Failed to get balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/positions")
async def get_positions(authenticated: bool = Depends(verify_api_key)):
    """Get open positions."""
    if not blofin_client:
        raise HTTPException(status_code=503, detail="BloFin client not initialized")
    
    try:
        positions = blofin_client.get_positions()
        return {"positions": positions}
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point."""
    import uvicorn
    
    # Validate critical configuration
    if not API_KEY:
        logger.warning("⚠️ API_KEY not set - authentication disabled!")
    
    logger.info(f"🚀 Starting server on {HOST}:{PORT}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
