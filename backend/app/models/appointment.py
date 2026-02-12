"""
Appointment Model

Represents scheduled patient appointments.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.base import BaseModel


class AppointmentStatus(str, Enum):
    """Appointment status values."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Types of appointments."""
    INITIAL = "initial_consultation"
    FOLLOW_UP = "follow_up"
    ANNUAL = "annual_physical"
    URGENT = "urgent_care"
    TELEHEALTH = "telehealth"
    PROCEDURE = "procedure"
    THERAPY = "therapy"
    OTHER = "other"


class Appointment(BaseModel):
    """
    Appointment model for patient scheduling.

    Links patients, providers, and time slots.
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

    # Scheduling
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(default=30)

    # Appointment Details
    appointment_type: Mapped[AppointmentType] = mapped_column(
        SQLEnum(AppointmentType),
        default=AppointmentType.FOLLOW_UP,
        nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus),
        default=AppointmentStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Clinical Information
    chief_complaint: Mapped[str | None] = mapped_column(Text())
    notes: Mapped[str | None] = mapped_column(Text())

    # Billing
    fee: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # Telehealth
    is_telehealth: Mapped[bool] = mapped_column(default=False)
    telehealth_link: Mapped[str | None] = mapped_column(String(500))

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(default=False)
    reminder_count: Mapped[int] = mapped_column(default=0)

    # Check-in
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    checked_in_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Cancellation
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text())

    # Extra metadata (JSON stored in database)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Relationships
    clinic = relationship("Clinic", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provider_appointments")
    encounter = relationship("Encounter", back_populates="appointment", uselist=False)

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, start='{self.start_time}', status='{self.status}')>"
