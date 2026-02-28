"""
Derived metric model.

Stores calculated financial metrics derived from financial statements.
Supports metric versioning to enable rule changes without losing historical
calculation context.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DerivedMetric(Base):
    """
    Calculated financial metric derived from financial statements.

    This entity stores computed metrics (e.g., ROE, debt-to-equity ratio) that
    are calculated from normalized financial statement data. The metric_version
    field enables versioning of calculation rules, ensuring reproducibility and
    allowing rule updates without losing historical calculation context.

    Attributes:
        id: Primary key, auto-incremented
        company_id: Foreign key to companies table
        fiscal_year: The fiscal year this metric applies to
        metric_name: Name of the metric (e.g., "roe", "debt_to_equity", "current_ratio")
        metric_value: Calculated numeric value of the metric
        metric_version: Version identifier for the calculation rule used
        calculated_at: Timestamp when this metric was calculated
        source_statement_id: Foreign key to the financial statement used for calculation
    """

    __tablename__ = "derived_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[Optional[float]] = mapped_column(Numeric(20, 6), nullable=True)
    metric_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    source_statement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("financial_statements_annual.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        """String representation of DerivedMetric instance."""
        return (
            f"<DerivedMetric(id={self.id}, company_id={self.company_id}, "
            f"metric_name='{self.metric_name}', fiscal_year={self.fiscal_year}, "
            f"value={self.metric_value}, version='{self.metric_version}')>"
        )
