"""
Patient Model

Represents patients in the healthcare system.
"""

import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import String, Date, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel, SoftDeleteMixin


class Gender(str, Enum):
    """Gender identity options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientStatus(str, Enum):
    """Patient status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"


class Patient(BaseModel, SoftDeleteMixin):
    """
    Patient model with PHI.

    All sensitive health information is encrypted at rest.
    """

    # Foreign Keys
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Medical Record Number (external identifier)
    mrn: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)

    # Personal Information (Basic - non-PHI)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_name: Mapped[str | None] = mapped_column(String(100))

    # Demographics
    date_of_birth: Mapped[date | None] = mapped_column(Date())
    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender),
        default=Gender.UNKNOWN,
        nullable=False,
    )
    sex_at_birth: Mapped[Gender] = mapped_column(
        SQLEnum(Gender),
        default=Gender.UNKNOWN,
    )

    # Contact Information
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    phone_type: Mapped[str | None] = mapped_column(String(20))  # mobile, home, work

    # Address (stored encrypted for PHI compliance)
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100), default="USA")

    # Emergency Contact
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50))
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(100))

    # Medical Information
    blood_type: Mapped[str | None] = mapped_column(String(10))
    allergies: Mapped[list[str] | None] = mapped_column(JSON, default=list)  # Stored as JSON
    medical_conditions: Mapped[list[str] | None] = mapped_column(JSON, default=list)

    # Status
    status: Mapped[PatientStatus] = mapped_column(
        SQLEnum(PatientStatus),
        default=PatientStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # No-show tracking
    no_show_count: Mapped[int] = mapped_column(default=0)

    # Portal access
    portal_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    clinic = relationship("Clinic", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    insurance_policies = relationship("PatientInsurance", back_populates="patient", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="patient")

    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int | None:
        """Calculate patient's age."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, name='{self.full_name}', mrn='{self.mrn}')>"


class PatientInsurance(BaseModel):
    """
    Patient insurance policy information.
    """

    # Foreign Keys
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Policy Information
    insurance_name: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False)
    group_number: Mapped[str | None] = mapped_column(String(100))

    # Member Information
    member_name: Mapped[str | None] = mapped_column(String(255))
    member_id: Mapped[str | None] = mapped_column(String(100))

    # Payer Information
    payer_id: Mapped[str | None] = mapped_column(String(20))  # Payer ID
    payer_name: Mapped[str | None] = mapped_column(String(255))

    # Coverage
    copay: Mapped[float | None] = mapped_column(default=0.0)
    deductible: Mapped[float | None] = mapped_column(default=0.0)

    # Status
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Expiration
    expiration_date: Mapped[date | None] = mapped_column(Date())

    # Relationships
    patient = relationship("Patient", back_populates="insurance_policies")

    def __repr__(self) -> str:
        return f"<PatientInsurance(id={self.id}, insurance='{self.insurance_name}')>"
