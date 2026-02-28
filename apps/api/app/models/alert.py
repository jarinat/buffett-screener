"""
Alert models.

Defines alert rules and events for monitoring company metrics and conditions.
AlertRule defines the conditions that trigger alerts, while AlertEvent tracks
when alerts are triggered with full event details for audit and analysis.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AlertRule(Base):
    """
    Definition of an alert rule.

    This entity defines the conditions and criteria for triggering alerts.
    The condition is stored as JSON to support flexible rule definitions while
    maintaining a structured history of alert configurations.

    Attributes:
        id: Primary key, auto-incremented
        name: Display name of the alert rule
        description: Detailed description of what this alert monitors
        condition_json: JSON object defining the alert conditions and thresholds
        company_id: Optional foreign key to a specific company (null for global alerts)
        created_at: Timestamp when this alert rule was created
        updated_at: Timestamp when this alert rule was last modified
        is_active: Whether this alert rule is currently active and monitoring
    """

    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        """String representation of AlertRule instance."""
        return (
            f"<AlertRule(id={self.id}, name='{self.name}', "
            f"company_id={self.company_id}, is_active={self.is_active})>"
        )


class AlertEvent(Base):
    """
    Record of a triggered alert event.

    This entity captures each instance when an alert rule is triggered,
    including the timestamp and detailed event data for full auditability.
    This allows historical analysis of alert patterns and conditions.

    Attributes:
        id: Primary key, auto-incremented
        alert_rule_id: Foreign key to the alert rule that was triggered
        company_id: Optional foreign key to the company involved in the alert
        triggered_at: Timestamp when this alert was triggered
        event_data_json: JSON object with detailed event data and context
    """

    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_rule_id: Mapped[int] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_data_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        """String representation of AlertEvent instance."""
        return (
            f"<AlertEvent(id={self.id}, alert_rule_id={self.alert_rule_id}, "
            f"company_id={self.company_id}, triggered_at={self.triggered_at})>"
        )
