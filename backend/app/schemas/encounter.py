from enum import Enum
"""
Encounter Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class EncounterType(str, Enum):
    """Encounter types."""
    OFFICE = "office_visit"
    TELEHEALTH = "telehealth"
    HOME = "home_visit"
    HOSPITAL = "hospital_consult"
    NURSING_HOME = "nursing_home_visit"
    EMERGENCY = "emergency_visit"


class EncounterCreate(BaseModel):
    """Request schema for creating an encounter."""
    patient_id: UUID
    provider_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    encounter_type: EncounterType = EncounterType.OFFICE
    chief_complaint: Optional[str] = None


class EncounterUpdate(BaseModel):
    """Request schema for updating an encounter."""
    status: Optional[str] = None
    chief_complaint: Optional[str] = None
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    vitals: Optional[dict] = None


class EncounterResponse(BaseModel):
    """Response schema for encounter."""
    id: UUID
    patient_id: UUID
    provider_id: UUID
    appointment_id: Optional[UUID]
    encounter_type: str
    status: str
    chief_complaint: Optional[str]
    subjective: Optional[str]
    objective: Optional[str]
    assessment: Optional[str]
    plan: Optional[str]
    vitals: Optional[dict]
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class EncounterListResponse(BaseModel):
    """Response schema for encounter list."""
    items: list[EncounterResponse]
    total: int
    skip: int
    limit: int
