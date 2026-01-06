"""
Shared data models for Discord Bot and Trading Server.

These models define the contract between services. Changes here affect both services.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TradeSide(Enum):
    """Trade direction."""
    LONG = "long"
    SHORT = "short"
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order types supported."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"


class TradeStatus(Enum):
    """Status of a trade signal."""
    RECEIVED = "received"
    PARSING = "parsing"
    VALIDATED = "validated"
    SENT = "sent"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class TradeSignal:
    """
    Parsed trade signal data.
    
    This is the core data structure passed from Discord Bot to Trading Server.
    """
    # Required fields
    symbol: str  # e.g., "BTC-USDT"
    side: str  # "long" or "short"
    
    # Optional trading parameters
    entry_price: Optional[float] = None  # Entry price (None = market order)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    size: Optional[float] = None  # Position size (contract qty or USD amount)
    
    # Metadata
    source: str = "discord"  # Source identifier
    signal_id: Optional[str] = None  # Unique ID for tracking
    timestamp: Optional[str] = None  # ISO format timestamp
    raw_message: Optional[str] = None  # Original Discord message
    
    def __post_init__(self):
        """Normalize and validate data after initialization."""
        # Normalize symbol to uppercase
        self.symbol = self.symbol.upper()
        
        # Normalize side
        self.side = self.side.lower()
        if self.side not in ["long", "short", "buy", "sell"]:
            raise ValueError(f"Invalid side: {self.side}. Must be long/short/buy/sell")
        
        # Set timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TradeSignal':
        """Create TradeSignal from dictionary."""
        return cls(**data)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate trade signal data.
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        if not self.symbol:
            return False, "Symbol is required"
        
        if not self.side:
            return False, "Side (long/short) is required"
        
        # Validate price values
        if self.entry_price is not None and self.entry_price <= 0:
            return False, "Entry price must be positive"
        
        if self.stop_loss is not None and self.stop_loss <= 0:
            return False, "Stop loss must be positive"
        
        if self.take_profit is not None and self.take_profit <= 0:
            return False, "Take profit must be positive"
        
        if self.size is not None and self.size <= 0:
            return False, "Size must be positive"
        
        # Validate price logic for long positions
        if self.side in ["long", "buy"]:
            if self.stop_loss and self.entry_price and self.stop_loss >= self.entry_price:
                return False, "Stop loss must be below entry price for long positions"
            if self.take_profit and self.entry_price and self.take_profit <= self.entry_price:
                return False, "Take profit must be above entry price for long positions"
        
        # Validate price logic for short positions
        if self.side in ["short", "sell"]:
            if self.stop_loss and self.entry_price and self.stop_loss <= self.entry_price:
                return False, "Stop loss must be above entry price for short positions"
            if self.take_profit and self.entry_price and self.take_profit >= self.entry_price:
                return False, "Take profit must be below entry price for short positions"
        
        return True, None


@dataclass
class TradeResponse:
    """
    Response from Trading Server after processing a trade signal.
    
    Sent back to Discord Bot for user notification.
    """
    success: bool
    signal_id: Optional[str] = None
    order_id: Optional[str] = None  # BloFin order ID
    message: str = ""
    status: str = TradeStatus.RECEIVED.value
    
    # Execution details
    executed_price: Optional[float] = None
    executed_size: Optional[float] = None
    executed_at: Optional[str] = None
    
    # Error details
    error_code: Optional[str] = None
    error_details: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TradeResponse':
        """Create TradeResponse from dictionary."""
        return cls(**data)


@dataclass
class HealthCheck:
    """Health check response for service monitoring."""
    service: str
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: str
    version: str = "1.0.0"
    details: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
