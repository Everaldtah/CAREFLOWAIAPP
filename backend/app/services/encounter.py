"""
Encounter Service
"""

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.encounter import Encounter


async def create_encounter(
    db: AsyncSession,
    patient_id: UUID,
    provider_id: UUID,
    clinic_id: UUID,
    encounter_type: str,
    chief_complaint: Optional[str] = None,
    appointment_id: Optional[UUID] = None,
) -> Encounter:
    """Create a new encounter."""
    encounter = Encounter(
        patient_id=patient_id,
        provider_id=provider_id,
        clinic_id=clinic_id,
        appointment_id=appointment_id,
        encounter_type=encounter_type,
        chief_complaint=chief_complaint,
        start_time=datetime.utcnow(),
    )
    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)
    return encounter


async def get_encounter_by_id(db: AsyncSession, encounter_id: UUID) -> Optional[Encounter]:
    """Get encounter by ID."""
    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    return result.scalar_one_or_none()


async def get_patient_encounters(
    db: AsyncSession,
    patient_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Encounter], int]:
    """List encounters for a patient."""
    query = select(Encounter).where(Encounter.patient_id == patient_id)

    count_result = await db.execute(
        select(func.count(Encounter.id)).where(Encounter.patient_id == patient_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Encounter.start_time.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def get_provider_encounters(
    db: AsyncSession,
    provider_id: UUID,
    clinic_id: UUID,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Encounter], int]:
    """List encounters for a provider."""
    query = select(Encounter).where(
        Encounter.provider_id == provider_id,
        Encounter.clinic_id == clinic_id,
    )

    if status:
        query = query.where(Encounter.status == status)

    if start_date:
        query = query.where(Encounter.start_time >= start_date)

    if end_date:
        query = query.where(Encounter.start_time <= end_date)

    count_result = await db.execute(
        select(func.count(Encounter.id)).where(Encounter.provider_id == provider_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Encounter.start_time.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def update_encounter(
    db: AsyncSession,
    encounter_id: UUID,
    data,
) -> Optional[Encounter]:
    """Update encounter."""
    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    encounter = result.scalar_one_or_none()

    if encounter:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(encounter, field, value)

        await db.commit()
        await db.refresh(encounter)

    return encounter


async def complete_encounter(
    db: AsyncSession,
    encounter_id: UUID,
) -> Optional[Encounter]:
    """Mark encounter as complete."""
    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    encounter = result.scalar_one_or_none()

    if encounter:
        encounter.status = "completed"
        encounter.end_time = datetime.utcnow()
        await db.commit()
        await db.refresh(encounter)

    return encounter
