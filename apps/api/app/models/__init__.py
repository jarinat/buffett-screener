"""
SQLAlchemy ORM models for the application.

This package contains all database entity models that inherit from the Base
declarative class defined in app.core.db. Each model represents a table in
the PostgreSQL database and defines the schema, relationships, and constraints.

Import models from this package to use them throughout the application.
"""

from app.models.company import Company
from app.models.listing import Listing

__all__ = [
    "Company",
    "Listing",
]
