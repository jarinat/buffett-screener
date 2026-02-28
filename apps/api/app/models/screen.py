"""
Screening models.

Defines screening criteria, execution runs, and individual company results.
Supports full reproducibility through rule versioning and detailed result storage.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ScreenDefinition(Base):
    """
    Definition of a screening strategy.

    This entity defines the criteria and rules for a stock screening strategy.
    The criteria are stored as JSON to support flexible rule definitions while
    maintaining a structured history of screen definitions.

    Attributes:
        id: Primary key, auto-incremented
        name: Display name of the screening strategy
        description: Detailed description of what this screen looks for
        criteria_json: JSON object defining the screening rules and thresholds
        created_at: Timestamp when this screen definition was created
        updated_at: Timestamp when this screen definition was last modified
        is_active: Whether this screen is currently active and available for use
    """

    __tablename__ = "screen_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criteria_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        """String representation of ScreenDefinition instance."""
        return (
            f"<ScreenDefinition(id={self.id}, name='{self.name}', is_active={self.is_active})>"
        )


class ScreenRun(Base):
    """
    Execution record of a screening run.

    This entity captures a single execution of a screening strategy, including
    the rule version bundle for full reproducibility. This allows historical
    screen runs to be analyzed with the exact rules that were in effect at the
    time of execution.

    Attributes:
        id: Primary key, auto-incremented
        screen_definition_id: Foreign key to the screen definition used
        rule_version_bundle: JSON snapshot of all rule versions used in this run
        executed_at: Timestamp when this screen was executed
        companies_evaluated: Total number of companies evaluated in this run
        companies_passed: Number of companies that passed the screening criteria
    """

    __tablename__ = "screen_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    screen_definition_id: Mapped[int] = mapped_column(
        ForeignKey("screen_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_version_bundle: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    companies_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    companies_passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        """String representation of ScreenRun instance."""
        return (
            f"<ScreenRun(id={self.id}, screen_id={self.screen_definition_id}, "
            f"executed_at={self.executed_at}, passed={self.companies_passed}/{self.companies_evaluated})>"
        )


class ScreenResult(Base):
    """
    Individual company result from a screening run.

    This entity stores the detailed results for a single company in a screening
    run, including whether it passed and the detailed metric values and
    pass/fail status for each screening criterion.

    Attributes:
        id: Primary key, auto-incremented
        screen_run_id: Foreign key to the screen run this result belongs to
        company_id: Foreign key to the company being evaluated
        passed: Whether the company passed all screening criteria
        result_details_json: JSON object with detailed results for each criterion
    """

    __tablename__ = "screen_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    screen_run_id: Mapped[int] = mapped_column(
        ForeignKey("screen_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    result_details_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        """String representation of ScreenResult instance."""
        return (
            f"<ScreenResult(id={self.id}, run_id={self.screen_run_id}, "
            f"company_id={self.company_id}, passed={self.passed})>"
        )
