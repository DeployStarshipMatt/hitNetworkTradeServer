"""Shared package for common models and utilities."""

from .models import (
    TradeSignal,
    TradeResponse,
    TradeSide,
    OrderType,
    TradeStatus,
    HealthCheck
)
from .authz import is_authorized_signal_poster

__all__ = [
    "is_authorized_signal_poster",
    "TradeSignal",
    "TradeResponse",
    "TradeSide",
    "OrderType",
    "TradeStatus",
    "HealthCheck"
]

__version__ = "1.0.0"
