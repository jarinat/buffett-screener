"""
Company entity model.

Represents a single business entity with its fundamental attributes.
A company can have multiple stock exchange listings (see Listing model).
"""

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Company(Base):
    """
    Core company entity representing a single business.

    This is the central entity that connects to listings, financial statements,
    and derived metrics. Each company represents a unique business regardless of
    how many stock exchanges it trades on.

    Attributes:
        id: Primary key, auto-incremented
        name: Common display name of the company
        legal_name: Official legal name
        country: Country of incorporation
        region: Geographic region (e.g., "North America", "Europe")
        domicile_market_scope: Market scope classification (e.g., "US", "International")
        sector: Business sector (e.g., "Technology", "Healthcare")
        industry: Specific industry within sector
        currency: Primary reporting currency (ISO 4217 code, e.g., "USD")
        is_active: Whether the company is currently active for screening
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domicile_market_scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        """String representation of Company instance."""
        return f"<Company(id={self.id}, name='{self.name}', ticker=N/A, is_active={self.is_active})>"
