"""
Financial Statement database models.

This module contains SQLAlchemy models for annual financial statements including
income statement, balance sheet, and cash flow statement data. Financial
statements are normalized and stored at the company level (not listing level),
using data from the primary listing.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.provider import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.provider import ProviderRawSnapshot


class FinancialStatementAnnual(Base):
    """
    Annual financial statement for a company.

    Represents a normalized annual financial statement combining data from
    income statement, balance sheet, and cash flow statement. Each record
    corresponds to a single fiscal year for a company. Data is sourced from
    provider APIs (e.g., yfinance, FMP) and normalized into a consistent
    schema for screening and analysis.

    All monetary values are stored in the company's reporting currency (see
    Company.currency field). Values are stored as Decimal for precision.
    Missing data is represented as NULL rather than zero to distinguish
    between "no data available" and "actual zero value".

    Each statement is linked to the raw provider snapshot for audit trail
    and data lineage tracking.
    """

    __tablename__ = "financial_statements_annual"

    statement_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for this financial statement (UUID)",
    )

    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.company_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to the company this statement belongs to",
    )

    fiscal_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        doc="Fiscal year end (e.g., 2023 for fiscal year ending in 2023)",
    )

    # Income Statement fields
    revenue: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Total revenue (top line) in company's reporting currency",
    )

    gross_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Gross profit (revenue minus cost of goods sold)",
    )

    operating_income: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Operating income (EBIT - earnings before interest and taxes)",
    )

    net_income: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Net income (bottom line after all expenses, interest, and taxes)",
    )

    eps_diluted: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
        doc="Diluted earnings per share",
    )

    # Balance Sheet fields
    total_assets: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Total assets",
    )

    total_liabilities: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Total liabilities",
    )

    shareholders_equity: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Shareholders' equity (total equity)",
    )

    # Cash Flow Statement fields
    free_cash_flow: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Free cash flow (operating cash flow minus capital expenditures)",
    )

    # Provenance fields
    source_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Provider name that sourced this data (e.g., 'yahoo_yfinance', 'fmp')",
    )

    source_snapshot_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("provider_raw_snapshots.snapshot_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Foreign key to the raw snapshot this statement was derived from",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        doc="Timestamp when this statement record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Timestamp when this statement record was last updated (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="financial_statements",
        doc="The company this financial statement belongs to",
    )

    source_snapshot: Mapped["ProviderRawSnapshot | None"] = relationship(
        "ProviderRawSnapshot",
        doc="The raw provider snapshot this statement was derived from",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<FinancialStatementAnnual("
            f"statement_id='{self.statement_id}', "
            f"company_id='{self.company_id}', "
            f"fiscal_year={self.fiscal_year}, "
            f"revenue={self.revenue}, "
            f"net_income={self.net_income}, "
            f"source_provider='{self.source_provider}'"
            f")>"
        )
