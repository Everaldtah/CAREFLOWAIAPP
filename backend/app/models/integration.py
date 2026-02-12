"""
Integration Model

Third-party system integrations (EHR, billing, etc.)
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class IntegrationProvider(str, Enum):
    """Integration providers."""
    EPIC = "epic"
    CERNER = "cerner"
    ATHENA = "athenahealth"
    ALLSCRIPTS = "allscripts"
    ECLINICAL_WORKS = "eclinical_works"
    NEXTGEN = "nextgen"
    DR_CHRONO = "dr_chrono"
    PRACTICE_FUSION = "practice_fusion"
    GENERIC_FHIR = "generic_fhir"
    CUSTOM = "custom"


class IntegrationStatus(str, Enum):
    """Integration status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"


class Integration(BaseModel):
    """
    Third-party integration configuration and status.

    Stores secure connection details for EHR and other systems.
    """

    # Foreign Keys
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Integration Details
    provider: Mapped[IntegrationProvider] = mapped_column(
        SQLEnum(IntegrationProvider),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(
        SQLEnum(IntegrationStatus),
        default=IntegrationStatus.INACTIVE,
        nullable=False,
    )

    # Connection (encrypted)
    # Sensitive credentials should be stored encrypted
    api_endpoint: Mapped[str | None] = mapped_column(String(500))
    api_key_encrypted: Mapped[str | None] = mapped_column(String(500))
    client_id: Mapped[str | None] = mapped_column(String(255))
    client_secret_encrypted: Mapped[str | None] = mapped_column(String(500))

    # Configuration
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)
    # Example: { "fhir_version": "R4", "sync_patients": true, "sync_appointments": true }

    # Sync Status
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync_status: Mapped[str | None] = mapped_column(String(50))
    last_sync_error: Mapped[str | None] = mapped_column(Text())

    # Webhooks
    webhook_url: Mapped[str | None] = mapped_column(String(500))
    webhook_secret: Mapped[str | None] = mapped_column(String(255))

    # Capabilities
    capabilities: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)),
        default=list,
    )  # ["patients", "appointments", "observations", etc.]

    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, provider='{self.provider}', status='{self.status}')>"
