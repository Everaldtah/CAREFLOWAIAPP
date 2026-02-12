"""
User Model

Represents all user types in the system: providers, nurses, staff, patients.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.core.base import BaseModel


class Role(str, Enum):
    """User roles with hierarchical permissions."""
    ADMIN = "admin"
    PROVIDER = "provider"  # Doctors, nurse practitioners
    NURSE = "nurse"
    STAFF = "staff"  # Medical assistants, techs
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"


class User(BaseModel):
    """
    User model for all system users.

    Supports multiple role types with different permission levels.
    """

    # Foreign Keys
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Personal Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))

    # Role & Permissions
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role),
        default=Role.PATIENT,
        nullable=False,
        index=True,
    )
    permissions: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)),
        default=list,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Provider-specific fields
    npi: Mapped[str | None] = mapped_column(String(20))  # National Provider Identifier
    specialization: Mapped[str | None] = mapped_column(String(255))
    license_number: Mapped[str | None] = mapped_column(String(100))

    # API Key (for integrations)
    api_key_hash: Mapped[str | None] = mapped_column(String(255), unique=True)

    # Settings
    preferences: Mapped[dict | None] = mapped_column(JSON, default=dict)
    timezone: Mapped[str] = mapped_column(String(50), default="America/New_York")

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    clinic = relationship("Clinic", back_populates="users")

    # Provider relationships
    provider_appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.provider_id",
        back_populates="provider",
    )
    provider_encounters = relationship(
        "Encounter",
        foreign_keys="Encounter.provider_id",
        back_populates="provider",
    )
    authored_notes = relationship(
        "Note",
        foreign_keys="Note.author_id",
        back_populates="author",
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
