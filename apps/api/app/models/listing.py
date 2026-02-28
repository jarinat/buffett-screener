"""
Listing entity model.

Represents a stock exchange listing for a company. A single company can have
multiple listings on different exchanges (e.g., primary listing on NYSE,
secondary listing on LSE).
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Listing(Base):
    """
    Stock exchange listing entity.

    Each listing represents one ticker symbol on one exchange for a company.
    Companies can have multiple listings across different exchanges.

    Attributes:
        id: Primary key, auto-incremented
        company_id: Foreign key to companies table
        ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
        exchange: Exchange name (e.g., "NASDAQ", "NYSE")
        mic: Market Identifier Code (ISO 10383 standard, e.g., "XNAS", "XNYS")
        currency: Trading currency for this listing (ISO 4217 code)
        is_primary: Whether this is the primary/main listing for the company
        is_active: Whether this listing is currently active for data fetching
    """

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    exchange: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mic: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        """String representation of Listing instance."""
        return f"<Listing(id={self.id}, ticker='{self.ticker}', exchange='{self.exchange}', company_id={self.company_id})>"
