"""Shared package for common models and utilities."""

from .models import (
    TradeSignal,
    TradeResponse,
    TradeSide,
    OrderType,
    TradeStatus,
    HealthCheck
)

__all__ = [
    "TradeSignal",
    "TradeResponse",
    "TradeSide",
    "OrderType",
    "TradeStatus",
    "HealthCheck"
]

__version__ = "1.0.0"
