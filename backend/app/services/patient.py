"""
Patient Service

Business logic for patient operations.
"""

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.tenant import Tenant


async def create_patient(
    db: AsyncSession,
    clinic_id: UUID,
    data,
) -> Patient:
    """Create a new patient."""
    patient = Patient(
        clinic_id=clinic_id,
        **data.model_dump(exclude_unset=True),
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def get_patient_by_id(db: AsyncSession, patient_id: UUID) -> Optional[Patient]:
    """Get patient by ID."""
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def get_patients_by_clinic(
    db: AsyncSession,
    clinic_id: UUID,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
) -> Tuple[list[Patient], int]:
    """List patients for a clinic."""
    query = select(Patient).where(Patient.clinic_id == clinic_id)

    if status_filter:
        query = query.where(Patient.status == status_filter)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    patients = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.clinic_id == clinic_id)
    )
    total = count_result.scalar() or 0

    return list(patients), total


async def search_patients(
    db: AsyncSession,
    clinic_id: UUID,
    query: str,
    limit: int = 20,
) -> list[dict]:
    """Search patients by name, email, phone, or MRN."""
    # Simplified search
    search_pattern = f"%{query}%"

    result = await db.execute(
        select(Patient).where(
            (Patient.clinic_id == clinic_id) & (
                (Patient.first_name.ilike(search_pattern)) |
                (Patient.last_name.ilike(search_pattern)) |
                (Patient.email.ilike(search_pattern)) |
                (Patient.phone.ilike(search_pattern)) |
                (Patient.mrn.ilike(search_pattern))
            )
        ).limit(limit)
    )

    patients = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "mrn": p.mrn,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "email": p.email,
            "phone": p.phone,
            "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
        }
        for p in patients
    ]


async def update_patient(
    db: AsyncSession,
    patient_id: UUID,
    data,
) -> Patient:
    """Update patient information."""
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if patient:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)

        await db.commit()
        await db.refresh(patient)

    return patient


async def delete_patient(db: AsyncSession, patient_id: UUID) -> bool:
    """Soft delete a patient."""
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if patient:
        patient.soft_delete()
        await db.commit()
        return True

    return False


async def get_patient_timeline(
    db: AsyncSession,
    patient_id: UUID,
) -> list[dict]:
    """Get patient timeline including appointments and encounters."""
    from app.models.appointment import Appointment
    from app.models.encounter import Encounter

    timeline = []

    # Get appointments
    apt_result = await db.execute(
        select(Appointment)
        .where(Appointment.patient_id == patient_id)
        .order_by(Appointment.start_time.desc())
        .limit(20)
    )
    for apt in apt_result.scalars():
        timeline.append({
            "type": "appointment",
            "date": apt.start_time.isoformat(),
            "status": apt.status,
            "details": {"appointment_type": apt.appointment_type, "id": str(apt.id)},
        })

    # Get encounters
    enc_result = await db.execute(
        select(Encounter)
        .where(Encounter.patient_id == patient_id)
        .order_by(Encounter.start_time.desc())
        .limit(10)
    )
    for enc in enc_result.scalars():
        timeline.append({
            "type": "encounter",
            "date": enc.start_time.isoformat(),
            "status": enc.status,
            "details": {"encounter_type": enc.encounter_type, "id": str(enc.id)},
        })

    # Sort by date
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return timeline
