from enum import Enum
"""
Patient Schemas

Request/response schemas for patient endpoints.
"""

from datetime import date, datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class Gender(str, Enum):
    """Gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientCreate(BaseModel):
    """Request schema for creating a patient."""
    mrn: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    preferred_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Gender = Gender.UNKNOWN
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class PatientUpdate(BaseModel):
    """Request schema for updating a patient."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class PatientResponse(BaseModel):
    """Response schema for patient data."""
    id: UUID
    mrn: Optional[str]
    first_name: str
    last_name: str
    preferred_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Gender
    email: Optional[str]
    phone: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    status: str
    no_show_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientSearchResponse(BaseModel):
    """Response schema for patient search results."""
    id: UUID
    mrn: Optional[str]
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[date]


class PatientListResponse(BaseModel):
    """Response schema for patient list."""
    items: list[PatientResponse]
    total: int
    skip: int
    limit: int


class InsuranceCreate(BaseModel):
    """Request schema for adding insurance."""
    insurance_name: str
    policy_number: str
    group_number: Optional[str] = None
    member_name: Optional[str] = None
    member_id: Optional[str] = None
    payer_id: Optional[str] = None
    copay: Optional[float] = None
    deductible: Optional[float] = None
    is_primary: bool = True
