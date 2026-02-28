"""
Provider-related database models.

This module contains SQLAlchemy models for tracking raw provider data snapshots
and provider metadata. All raw API responses are stored for debugging and replay.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class ProviderRawSnapshot(Base):
    """
    Raw snapshot of a provider API response.

    Stores the complete, unmodified response from external data providers
    (Yahoo Finance, FMP, etc.) for debugging, auditing, and replay capabilities.
    Every provider API call should create a corresponding snapshot.

    This enables:
    - Debugging data quality issues by inspecting raw responses
    - Replaying normalization logic without re-fetching
    - Tracking provider API changes over time
    - Audit trail for regulatory compliance
    """

    __tablename__ = "provider_raw_snapshots"

    snapshot_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for this snapshot (UUID)",
    )

    provider_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Name of the data provider (e.g., 'yahoo_finance', 'fmp')",
    )

    provider_entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Type of entity fetched (e.g., 'company_profile', 'income_statement', 'price_history')",
    )

    provider_entity_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Provider's identifier for the entity (e.g., ticker symbol, company ID)",
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        doc="Timestamp when the data was fetched from the provider (UTC)",
    )

    payload_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        doc="Complete raw JSON response from the provider API",
    )

    http_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="HTTP status code of the provider API response (if applicable)",
    )

    ingestion_run_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        doc="ID of the ingestion run that created this snapshot (for batch tracking)",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<ProviderRawSnapshot("
            f"snapshot_id='{self.snapshot_id}', "
            f"provider='{self.provider_name}', "
            f"type='{self.provider_entity_type}', "
            f"key='{self.provider_entity_key}', "
            f"fetched_at={self.fetched_at}"
            f")>"
        )
