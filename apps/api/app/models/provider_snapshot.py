"""
Provider raw snapshot model.

Stores the raw JSON payload from external data providers for full auditability
and replay capability. This allows re-processing with updated normalization
rules without re-fetching from providers.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ProviderRawSnapshot(Base):
    """
    Raw snapshot from an external data provider.

    This entity stores the complete, unmodified response from data providers
    (e.g., financial data APIs). Storing raw payloads enables:
    - Full audit trail of data sources
    - Replay capability with updated normalization logic
    - Debugging and comparison of provider data changes
    - Independence from provider API availability for historical data

    Attributes:
        id: Primary key, auto-incremented
        provider_name: Name of the data provider (e.g., "alpha_vantage", "fmp")
        provider_entity_type: Type of entity fetched (e.g., "financials", "company_overview")
        provider_entity_key: Provider-specific identifier for the entity
        fetched_at: Timestamp when the data was fetched from the provider
        payload_json: Full JSON response from the provider (stored as JSONB for querying)
        http_status: HTTP status code of the provider response
        ingestion_run_id: Optional identifier for the ingestion batch/run
    """

    __tablename__ = "provider_raw_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    provider_entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_entity_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    payload_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ingestion_run_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    def __repr__(self) -> str:
        """String representation of ProviderRawSnapshot instance."""
        return (
            f"<ProviderRawSnapshot(id={self.id}, provider='{self.provider_name}', "
            f"type='{self.provider_entity_type}', fetched_at={self.fetched_at})>"
        )
