"""
Tenant Schemas
"""

from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Plan(str, Enum):
    """Subscription plans."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantCreate(BaseModel):
    """Request schema for creating a tenant."""
    name: str
    slug: str
    plan: Plan = Plan.BASIC


class TenantUpdate(BaseModel):
    """Request schema for updating a tenant."""
    name: Optional[str] = None
    plan: Optional[Plan] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    """Response schema for tenant."""
    id: UUID
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: str
    updated_at: str
