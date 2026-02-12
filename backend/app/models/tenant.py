"""
Tenant Model

Represents a multi-tenant organization (healthcare system, hospital network, etc.)
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import BaseModel


class Plan(str, Enum):
    """Subscription plan types."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Tenant(BaseModel):
    """
    Tenant model for multi-tenancy.

    Represents a healthcare organization or practice group.
    Each tenant is isolated at the database level.
    """

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Subscription
    plan: Mapped[Plan] = mapped_column(String(50), default=Plan.BASIC, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contact
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))

    # Settings (JSON stored in database)
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationships
    clinics = relationship("Clinic", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name='{self.name}', plan='{self.plan}')>"
