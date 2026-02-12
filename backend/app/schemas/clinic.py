"""
Clinic Schemas
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ClinicCreate(BaseModel):
    """Request schema for creating a clinic."""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ClinicUpdate(BaseModel):
    """Request schema for updating a clinic."""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class ClinicResponse(BaseModel):
    """Response schema for clinic."""
    id: UUID
    tenant_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
