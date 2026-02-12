"""
Clinic Service
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic


async def create_clinic(
    db: AsyncSession,
    tenant_id: UUID,
    name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> Clinic:
    """Create a new clinic."""
    clinic = Clinic(
        tenant_id=tenant_id,
        name=name,
        address=address,
        phone=phone,
        email=email,
    )
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic


async def get_clinic_by_id(db: AsyncSession, clinic_id: UUID) -> Optional[Clinic]:
    """Get clinic by ID."""
    result = await db.execute(
        select(Clinic).where(Clinic.id == clinic_id)
    )
    return result.scalar_one_or_none()


async def list_tenant_clinics(
    db: AsyncSession,
    tenant_id: UUID,
) -> List[Clinic]:
    """List all clinics for a tenant."""
    result = await db.execute(
        select(Clinic).where(Clinic.tenant_id == tenant_id)
    )
    return list(result.scalars().all())


async def update_clinic(
    db: AsyncSession,
    clinic_id: UUID,
    data,
) -> Optional[Clinic]:
    """Update clinic."""
    result = await db.execute(
        select(Clinic).where(Clinic.id == clinic_id)
    )
    clinic = result.scalar_one_or_none()

    if clinic:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(clinic, field, value)

        await db.commit()
        await db.refresh(clinic)

    return clinic
