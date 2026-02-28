"""
Data provider abstractions.

This package defines abstract base classes for all data providers, ensuring
a consistent interface regardless of the underlying data source. This allows
the screening engine to remain decoupled from specific provider implementations.
"""

from app.providers.base import CompanyUniverseProvider

__all__ = [
    "CompanyUniverseProvider",
]
