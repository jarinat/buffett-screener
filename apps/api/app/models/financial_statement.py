"""
Financial statement model.

Represents normalized annual financial data for companies, extracted and
normalized from provider raw snapshots. This layer provides a consistent
schema regardless of the source provider.
"""

from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class FinancialStatementAnnual(Base):
    """
    Normalized annual financial statement data.

    This entity stores standardized annual financial metrics extracted from
    provider raw snapshots. All values are normalized to a consistent format
    regardless of the source provider, enabling reliable metric calculation
    and screening.

    Attributes:
        id: Primary key, auto-incremented
        company_id: Foreign key to companies table
        fiscal_year: The fiscal year for this statement (e.g., 2023)
        revenue: Total revenue/sales for the fiscal year
        gross_profit: Revenue minus cost of goods sold
        net_income: Net profit after all expenses and taxes
        operating_income: Operating profit before interest and taxes
        eps_diluted: Diluted earnings per share
        total_assets: Total assets on the balance sheet
        total_liabilities: Total liabilities on the balance sheet
        shareholders_equity: Total shareholders' equity
        free_cash_flow: Cash flow available after capital expenditures
        source_provider: Name of the provider this data was sourced from
        source_snapshot_id: Foreign key to the provider_raw_snapshots table
    """

    __tablename__ = "financial_statements_annual"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    revenue: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    gross_profit: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    net_income: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    operating_income: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    eps_diluted: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True)
    total_assets: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    total_liabilities: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    shareholders_equity: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    free_cash_flow: Mapped[Optional[float]] = mapped_column(Numeric(20, 2), nullable=True)
    source_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    source_snapshot_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("provider_raw_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        """String representation of FinancialStatementAnnual instance."""
        return (
            f"<FinancialStatementAnnual(id={self.id}, company_id={self.company_id}, "
            f"fiscal_year={self.fiscal_year}, revenue={self.revenue})>"
        )
