"""
Appointment Service
"""

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment


async def create_appointment(
    db: AsyncSession,
    clinic_id: UUID,
    data,
) -> Appointment:
    """Create a new appointment."""
    appointment = Appointment(
        clinic_id=clinic_id,
        **data.model_dump(),
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def get_appointment_by_id(db: AsyncSession, appointment_id: UUID) -> Optional[Appointment]:
    """Get appointment by ID."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    return result.scalar_one_or_none()


async def get_appointments_by_clinic(
    db: AsyncSession,
    clinic_id: UUID,
    provider_id: Optional[UUID] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Appointment], int]:
    """List appointments for a clinic."""
    query = select(Appointment).where(Appointment.clinic_id == clinic_id)

    if provider_id:
        query = query.where(Appointment.provider_id == provider_id)

    if status:
        query = query.where(Appointment.status == status)

    if start_date:
        query = query.where(Appointment.start_time >= start_date)

    if end_date:
        query = query.where(Appointment.start_time <= end_date)

    # Get total count
    count_result = await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.clinic_id == clinic_id
        )
    )
    total = count_result.scalar() or 0

    # Get results
    query = query.order_by(Appointment.start_time.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def get_appointments_by_patient(
    db: AsyncSession,
    patient_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Appointment], int]:
    """List appointments for a patient."""
    query = select(Appointment).where(Appointment.patient_id == patient_id)

    count_result = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.patient_id == patient_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Appointment.start_time.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def check_appointment_conflicts(
    db: AsyncSession,
    provider_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_appointment_id: Optional[UUID] = None,
) -> bool:
    """Check for appointment conflicts."""
    query = select(Appointment).where(
        and_(
            Appointment.provider_id == provider_id,
            Appointment.status.not_in(["cancelled", "no_show"]),
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
        )
    )

    if exclude_appointment_id:
        query = query.where(Appointment.id != exclude_appointment_id)

    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def get_calendar_view(
    db: AsyncSession,
    clinic_id: UUID,
    provider_id: Optional[UUID],
    start: datetime,
    end: datetime,
) -> list[dict]:
    """Get calendar events for date range."""
    query = select(Appointment).where(
        and_(
            Appointment.clinic_id == clinic_id,
            Appointment.start_time >= start,
            Appointment.start_time <= end,
        )
    )

    if provider_id:
        query = query.where(Appointment.provider_id == provider_id)

    result = await db.execute(query)
    appointments = result.scalars().all()

    events = []
    for apt in appointments:
        events.append({
            "id": str(apt.id),
            "title": f"{apt.appointment_type.replace('_', ' ').title()}",
            "start": apt.start_time.isoformat(),
            "end": apt.end_time.isoformat(),
            "status": apt.status,
            "type": apt.appointment_type,
            "patient_id": str(apt.patient_id),
            "provider_id": str(apt.provider_id),
        })

    return events


async def get_provider_availability(
    db: AsyncSession,
    provider_id: UUID,
    date: datetime,
) -> list[dict]:
    """Get available time slots for a provider on a date."""
    # Simplified - return standard business hour slots
    slots = []
    start_hour = 9
    end_hour = 17

    for hour in range(start_hour, end_hour):
        for minute in [0, 15, 30, 45]:
            slots.append({
                "start": f"{hour:02d}:{minute:02d}",
                "end": f"{hour:02d}:{minute + 15:02d}",
                "available": True,
            })

    return slots


async def create_available_slot(
    db: AsyncSession,
    provider_id: UUID,
    start_time: datetime,
    end_time: datetime,
    recurring: Optional[str] = None,
) -> list[dict]:
    """Create available time slot."""
    # In production, would store in availability table
    return []


async def update_appointment(
    db: AsyncSession,
    appointment_id: UUID,
    data,
) -> Optional[Appointment]:
    """Update appointment."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if appointment:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(appointment, field, value)

        await db.commit()
        await db.refresh(appointment)

    return appointment


async def cancel_appointment(
    db: AsyncSession,
    appointment_id: UUID,
) -> Optional[Appointment]:
    """Cancel an appointment."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if appointment:
        appointment.status = "cancelled"
        appointment.cancelled_at = datetime.utcnow()
        await db.commit()
        await db.refresh(appointment)

    return appointment
