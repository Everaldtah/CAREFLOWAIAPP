"""
Tenant Management Endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_admin
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.services.tenant import (
    create_tenant,
    get_tenant_by_id,
    update_tenant,
)

router = APIRouter()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_endpoint(
    data: TenantCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Create a new tenant (super admin only)."""
    tenant = await create_tenant(
        db=db,
        name=data.name,
        slug=data.slug,
        plan=data.plan,
    )
    return tenant


@router.get("/{tenant_id}")
async def get_tenant_endpoint(
    tenant_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Get tenant details."""
    tenant = await get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant


@router.patch("/{tenant_id}")
async def update_tenant_endpoint(
    tenant_id: UUID,
    data: TenantUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Update tenant details."""
    tenant = await update_tenant(db, tenant_id, data)
    return tenant
