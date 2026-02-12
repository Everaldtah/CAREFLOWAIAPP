from enum import Enum
"""
User Schemas
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    PROVIDER = "provider"
    NURSE = "nurse"
    STAFF = "staff"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"


class UserCreate(BaseModel):
    """Request schema for creating a user."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: Role = Role.PATIENT
    phone: Optional[str] = None
    clinic_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    """Request schema for updating a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Response schema for user."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool
    tenant_id: Optional[UUID]
    clinic_id: Optional[UUID]
    created_at: str
    updated_at: str
