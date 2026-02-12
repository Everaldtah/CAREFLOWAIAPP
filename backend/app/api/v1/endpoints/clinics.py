"""
Clinic Management Endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_admin
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse
from app.services.clinic import (
    create_clinic,
    get_clinic_by_id,
    update_clinic,
    list_tenant_clinics,
)

router = APIRouter()


@router.post("/", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic_endpoint(
    data: ClinicCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Create a new clinic (requires admin)."""
    clinic = await create_clinic(
        db=db,
        tenant_id=current_user.tenant_id,
        name=data.name,
        address=data.address,
        phone=data.phone,
        email=data.email,
    )
    return clinic


@router.get("/")
async def list_clinics(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """List all clinics in the tenant."""
    clinics = await list_tenant_clinics(
        db=db,
        tenant_id=current_user.tenant_id,
    )
    return {"items": clinics}


@router.get("/{clinic_id}")
async def get_clinic_endpoint(
    clinic_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Get clinic details."""
    clinic = await get_clinic_by_id(db, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )
    return clinic


@router.patch("/{clinic_id}")
async def update_clinic_endpoint(
    clinic_id: UUID,
    data: ClinicUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Update clinic details."""
    clinic = await update_clinic(db, clinic_id, data)
    return clinic
