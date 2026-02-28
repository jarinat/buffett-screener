<<<<<<< HEAD
"""Provider adapters for external data sources."""

from app.providers.base import BaseProvider, RateLimiter
from app.providers.yahoo_yfinance import YahooYFinanceProvider

__all__ = [
    "BaseProvider",
    "RateLimiter",
    "YahooYFinanceProvider",
=======
"""
Data provider abstractions.

This package defines abstract base classes for all data providers, ensuring
a consistent interface regardless of the underlying data source. This allows
the screening engine to remain decoupled from specific provider implementations.
"""

from app.providers.base import (
    CompanyUniverseProvider,
    FundamentalsProvider,
    PriceHistoryProvider,
)
from app.providers.registry import ProviderRegistry, get_provider_registry

__all__ = [
    "CompanyUniverseProvider",
    "FundamentalsProvider",
    "PriceHistoryProvider",
    "ProviderRegistry",
    "get_provider_registry",
>>>>>>> origin/main
]
