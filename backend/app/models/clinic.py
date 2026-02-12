"""
Clinic Model

Represents a specific clinic or practice location within a tenant.
"""

import uuid
from sqlalchemy import String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class Clinic(BaseModel):
    """
    Clinic model representing a healthcare facility.

    Part of a tenant (organization) with multiple locations possible.
    """

    # Foreign Keys
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    npi: Mapped[str | None] = mapped_column(String(20), unique=True)  # National Provider Identifier

    # Contact
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    fax: Mapped[str | None] = mapped_column(String(50))

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100), default="USA")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Settings
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationships
    tenant = relationship("Tenant", back_populates="clinics")
    users = relationship("User", back_populates="clinic")
    patients = relationship("Patient", back_populates="clinic")
    appointments = relationship("Appointment", back_populates="clinic")
    encounters = relationship("Encounter", back_populates="clinic")

    def __repr__(self) -> str:
        return f"<Clinic(id={self.id}, name='{self.name}')>"
