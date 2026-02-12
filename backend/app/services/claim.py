"""
Claim Service
"""

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim


async def create_claim(
    db: AsyncSession,
    encounter_id: UUID,
    created_by: UUID,
    insurance_id: Optional[UUID] = None,
) -> Claim:
    """Create a new claim."""
    claim = Claim(
        encounter_id=encounter_id,
        insurance_id=insurance_id,
        submitted_by_id=created_by,
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim


async def get_claims_by_clinic(
    db: AsyncSession,
    clinic_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Claim], int]:
    """List claims for a clinic."""
    from app.models.encounter import Encounter

    query = (
        select(Claim)
        .join(Encounter, Claim.encounter_id == Encounter.id)
        .where(Encounter.clinic_id == clinic_id)
    )

    count_result = await db.execute(
        select(func.count(Claim.id))
        .join(Encounter, Claim.encounter_id == Encounter.id)
        .where(Encounter.clinic_id == clinic_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def submit_claim(
    db: AsyncSession,
    claim_id: UUID,
) -> Optional[Claim]:
    """Submit claim to insurance."""
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()

    if claim:
        claim.status = "submitted"
        await db.commit()
        await db.refresh(claim)

    return claim
