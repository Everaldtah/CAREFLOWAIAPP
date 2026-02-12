"""
Tenant Service
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


async def create_tenant(
    db: AsyncSession,
    name: str,
    slug: str,
    plan: str = "basic",
) -> Tenant:
    """Create a new tenant."""
    tenant = Tenant(
        name=name,
        slug=slug,
        plan=plan,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


async def get_tenant_by_id(db: AsyncSession, tenant_id: UUID) -> Optional[Tenant]:
    """Get tenant by ID."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    return result.scalar_one_or_none()


async def update_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    data,
) -> Optional[Tenant]:
    """Update tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tenant, field, value)

        await db.commit()
        await db.refresh(tenant)

    return tenant
