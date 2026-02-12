from enum import Enum
"""
Claim Schemas
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ClaimStatus(str, Enum):
    """Claim status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    DENIED = "denied"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class ClaimCreate(BaseModel):
    """Request schema for creating a claim."""
    encounter_id: UUID
    insurance_id: Optional[UUID] = None


class ClaimUpdate(BaseModel):
    """Request schema for updating a claim."""
    status: Optional[str] = None
    denial_reason: Optional[str] = None


class ClaimResponse(BaseModel):
    """Response schema for claim."""
    id: UUID
    encounter_id: UUID
    patient_id: UUID
    insurance_id: Optional[UUID]
    claim_number: Optional[str]
    status: str
    date_of_service: date
    total_charge: float
    allowed_amount: Optional[float]
    paid_amount: Optional[float]
    patient_responsibility: Optional[float]
    created_at: datetime
    updated_at: datetime
