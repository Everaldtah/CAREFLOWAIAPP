"""
Claim Model

Insurance claims for medical services.
"""

import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import String, Date, Text, ForeignKey, Enum as SQLEnum, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class ClaimStatus(str, Enum):
    """Insurance claim status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    DENIED = "denied"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class Claim(BaseModel):
    """
    Insurance claim model.

    Tracks claims submitted to insurance payers.
    """

    # Foreign Keys
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    insurance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patient_insurances.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Claim Details
    claim_number: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[ClaimStatus] = mapped_column(
        SQLEnum(ClaimStatus),
        default=ClaimStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # Dates
    date_of_service: Mapped[date] = mapped_column(Date(), nullable=False)
    submission_date: Mapped[date | None] = mapped_column(Date())
    adjudication_date: Mapped[date | None] = mapped_column(Date())

    # Financials
    total_charge: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    allowed_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    paid_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    patient_responsibility: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # Payer Information
    payer_name: Mapped[str | None] = mapped_column(String(255))
    payer_id: Mapped[str | None] = mapped_column(String(50))

    # Submission
    submitted_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    submitted_via: Mapped[str | None] = mapped_column(String(50))  # 'electronic', 'paper'

    # Response
    denial_reason: Mapped[str | None] = mapped_column(Text())
    denial_code: Mapped[str | None] = mapped_column(String(50))

    # Notes
    internal_notes: Mapped[str | None] = mapped_column(Text())

    # Extra tracking metadata
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationships
    lines = relationship("ClaimLine", back_populates="claim", cascade="all, delete-orphan")

    @property
    def is_paid(self) -> bool:
        """Check if claim is fully paid."""
        return self.status == ClaimStatus.APPROVED and self.paid_amount is not None

    def __repr__(self) -> str:
        return f"<Claim(id={self.id}, number='{self.claim_number}', status='{self.status}')>"


class ClaimLine(BaseModel):
    """
    Individual line items within a claim.
    """

    # Foreign Keys
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Line Number
    line_number: Mapped[int] = mapped_column(default=1)

    # Codes
    procedure_code: Mapped[str] = mapped_column(String(20), nullable=False)  # CPT/HCPCS
    modifier_1: Mapped[str | None] = mapped_column(String(10))
    modifier_2: Mapped[str | None] = mapped_column(String(10))
    diagnosis_code_pointer: Mapped[str | None] = mapped_column(String(20))  # ICD-10 reference

    # Description
    description: Mapped[str | None] = mapped_column(String(255))

    # Financials
    charge_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    allowed_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    paid_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # Units
    units: Mapped[int] = mapped_column(default=1)

    # Relationships
    claim = relationship("Claim", back_populates="lines")

    def __repr__(self) -> str:
        return f"<ClaimLine(id={self.id}, code='{self.procedure_code}', charge={self.charge_amount})>"
