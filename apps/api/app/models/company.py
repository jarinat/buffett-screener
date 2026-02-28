"""
Company and Listing database models.

This module contains SQLAlchemy models for companies and their stock exchange
listings. A Company represents the business entity (e.g., Apple Inc.), while
Listing represents a specific stock ticker on a specific exchange (e.g., AAPL
on NASDAQ). A single company can have multiple listings (different exchanges,
different share classes, etc.).
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.provider import Base

if TYPE_CHECKING:
    from app.models.financial_statement import FinancialStatementAnnual


class Company(Base):
    """
    Business entity that issues stock.

    Represents a company as a business entity with its fundamental attributes
    like name, sector, and industry. A company can have multiple stock listings
    across different exchanges or share classes. The company_id is the primary
    identifier used to link financial data, metrics, and other company-specific
    information.

    This model stores normalized company master data derived from various
    providers. The source of truth for any field can be tracked through
    provider snapshots and metadata.
    """

    __tablename__ = "companies"

    company_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the company (UUID)",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Common company name (e.g., 'Apple Inc.', 'Microsoft Corporation')",
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Official legal name of the company if different from common name",
    )

    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
        doc="ISO 3166-1 alpha-2 country code (e.g., 'US', 'CA', 'GB')",
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Business sector (e.g., 'Technology', 'Healthcare', 'Financial Services')",
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Specific industry within sector (e.g., 'Software', 'Biotechnology', 'Banks')",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="ISO 4217 currency code for company's reporting currency (e.g., 'USD', 'EUR', 'JPY')",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        doc="Whether the company is currently active (True) or delisted/defunct (False)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        doc="Timestamp when this company record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Timestamp when this company record was last updated (UTC)",
    )

    # Relationships
    listings: Mapped[list["Listing"]] = relationship(
        "Listing",
        back_populates="company",
        doc="All stock exchange listings for this company",
    )

    financial_statements: Mapped[list["FinancialStatementAnnual"]] = relationship(
        "FinancialStatementAnnual",
        back_populates="company",
        doc="Annual financial statements for this company",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Company("
            f"company_id='{self.company_id}', "
            f"name='{self.name}', "
            f"country='{self.country}', "
            f"sector='{self.sector}', "
            f"is_active={self.is_active}"
            f")>"
        )


class Listing(Base):
    """
    Stock exchange listing for a company.

    Represents a specific ticker symbol on a specific exchange. A company can
    have multiple listings (e.g., dual-listed on NYSE and LSE, or different
    share classes like BRK.A and BRK.B). The is_primary flag indicates which
    listing is the canonical one for fetching financial data.

    This model enables tracking companies across multiple exchanges and handling
    complex scenarios like ADRs, dual listings, and share class structures.
    """

    __tablename__ = "listings"

    listing_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for this listing (UUID)",
    )

    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.company_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to the company that owns this listing",
    )

    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Ticker symbol (e.g., 'AAPL', 'MSFT', 'BRK.B')",
    )

    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Stock exchange code (e.g., 'NASDAQ', 'NYSE', 'LSE', 'TSX')",
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        doc="Whether this is the primary listing for fetching financial data (only one per company should be True)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        doc="Whether this listing is currently active (True) or delisted (False)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        doc="Timestamp when this listing record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Timestamp when this listing record was last updated (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="listings",
        doc="The company that owns this listing",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Listing("
            f"listing_id='{self.listing_id}', "
            f"ticker='{self.ticker}', "
            f"exchange='{self.exchange}', "
            f"company_id='{self.company_id}', "
            f"is_primary={self.is_primary}, "
            f"is_active={self.is_active}"
            f")>"
        )
