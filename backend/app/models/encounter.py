"""
Encounter Model

Represents a clinical visit/encounter (face-to-face or virtual).
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class EncounterStatus(str, Enum):
    """Encounter status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EncounterType(str, Enum):
    """Types of encounters."""
    OFFICE = "office_visit"
    TELEHEALTH = "telehealth"
    HOME = "home_visit"
    HOSPITAL = "hospital_consult"
    NURSING_HOME = "nursing_home_visit"
    EMERGENCY = "emergency_visit"


class Encounter(BaseModel):
    """
    Clinical encounter model.

    Represents a patient visit for clinical care.
    """

    # Foreign Keys
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    # Encounter Details
    encounter_type: Mapped[EncounterType] = mapped_column(
        SQLEnum(EncounterType),
        default=EncounterType.OFFICE,
        nullable=False,
    )
    status: Mapped[EncounterStatus] = mapped_column(
        SQLEnum(EncounterStatus),
        default=EncounterStatus.SCHEDULED,
        nullable=False,
        index=True,
    )

    # Clinical Information
    chief_complaint: Mapped[str | None] = mapped_column(Text())
    subjective: Mapped[str | None] = mapped_column(Text())  # Patient's reported symptoms
    objective: Mapped[str | None] = mapped_column(Text())  # Provider's observations
    assessment: Mapped[str | None] = mapped_column(Text())  # Diagnosis/impression
    plan: Mapped[str | None] = mapped_column(Text())  # Treatment plan

    # Vitals (stored as JSON)
    vitals: Mapped[dict | None] = mapped_column(JSON, default=dict)
    # Example: { "blood_pressure": "120/80", "temperature": 98.6, "weight": 180, ... }

    # Timing
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    # Billing
    is_billable: Mapped[bool] = mapped_column(default=True)

    # Relationships
    clinic = relationship("Clinic", back_populates="encounters")
    patient = relationship("Patient", back_populates="encounters")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provider_encounters")
    appointment = relationship("Appointment", back_populates="encounter")
    notes = relationship("Note", back_populates="encounter", cascade="all, delete-orphan")

    @property
    def duration_minutes(self) -> int | None:
        """Calculate encounter duration in minutes."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    def __repr__(self) -> str:
        return f"<Encounter(id={self.id}, type='{self.encounter_type}', status='{self.status}')>"
