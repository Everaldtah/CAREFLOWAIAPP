from enum import Enum
"""
Appointment Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AppointmentStatus(str, Enum):
    """Appointment status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Appointment types."""
    INITIAL = "initial_consultation"
    FOLLOW_UP = "follow_up"
    ANNUAL = "annual_physical"
    URGENT = "urgent_care"
    TELEHEALTH = "telehealth"
    PROCEDURE = "procedure"
    THERAPY = "therapy"
    OTHER = "other"


class AppointmentCreate(BaseModel):
    """Request schema for creating an appointment."""
    patient_id: UUID
    provider_id: UUID
    start_time: datetime
    end_time: datetime
    appointment_type: AppointmentType = AppointmentType.FOLLOW_UP
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    is_telehealth: bool = False
    fee: Optional[float] = None


class AppointmentUpdate(BaseModel):
    """Request schema for updating an appointment."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    provider_id: Optional[UUID] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[str] = None
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Response schema for appointment."""
    id: UUID
    patient_id: UUID
    provider_id: UUID
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    appointment_type: str
    status: str
    chief_complaint: Optional[str]
    notes: Optional[str]
    is_telehealth: bool
    telehealth_link: Optional[str]
    fee: Optional[float]
    created_at: datetime
    updated_at: datetime


class AppointmentListResponse(BaseModel):
    """Response schema for appointment list."""
    items: list[AppointmentResponse]
    total: int
    skip: int
    limit: int


class CalendarEvent(BaseModel):
    """Calendar event."""
    id: UUID
    title: str
    start: datetime
    end: datetime
    status: str
    type: str
    patient_name: str
    provider_name: str
    is_telehealth: bool


class CalendarViewResponse(BaseModel):
    """Response schema for calendar view."""
    start: datetime
    end: datetime
    events: list[CalendarEvent]


class SlotCreate(BaseModel):
    """Request schema for creating availability slots."""
    provider_id: UUID
    start_time: datetime
    end_time: datetime
    recurring: Optional[str] = None  # 'daily', 'weekly', 'monthly'


class AvailabilitySlot(BaseModel):
    """Available time slot."""
    start: datetime
    end: datetime
    available: bool


class AvailabilityResponse(BaseModel):
    """Response schema for availability."""
    provider_id: str
    date: str
    available_slots: list[AvailabilitySlot]
