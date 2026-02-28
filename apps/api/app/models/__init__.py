"""
Data models for the provider abstraction layer.

This package contains canonical data models that are provider-agnostic.
All data providers must return these standard models, ensuring the screening
engine is decoupled from any specific data source.
"""

from app.models.company import CompanyInfo, Listing

__all__ = [
    "CompanyInfo",
    "Listing",
]
