"""
Appointment & Scheduling Endpoints

Handles appointment scheduling, calendar views, and availability.
"""

from datetime import datetime, timedelta
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, Pagination
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse,
    CalendarViewResponse,
    AvailabilityResponse,
    SlotCreate,
)
from app.services.appointment import (
    create_appointment,
    get_appointment_by_id,
    get_appointments_by_clinic,
    get_appointments_by_patient,
    get_calendar_view,
    get_provider_availability,
    create_available_slot,
    cancel_appointment,
    update_appointment,
    check_appointment_conflicts,
)
from app.services.audit import log_phi_access

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment_endpoint(
    data: AppointmentCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new appointment.

    - Validates provider availability
    - Checks for conflicts
    - Sends confirmation
    - Optionally triggers AI scheduling optimization
    """
    # Check for conflicts
    has_conflict = await check_appointment_conflicts(
        db=db,
        provider_id=data.provider_id,
        start_time=data.start_time,
        end_time=data.end_time,
    )

    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is already booked",
        )

    appointment = await create_appointment(
        db=db,
        clinic_id=current_user.clinic_id,
        data=data,
    )

    # Log creation
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="appointment",
        resource_id=appointment.id,
        action="create",
    )

    # TODO: Send confirmation email/SMS

    return appointment


@router.get("/", response_model=AppointmentListResponse)
async def list_appointments(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
    patient_id: UUID | None = Query(None),
    provider_id: UUID | None = Query(None),
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> Any:
    """
    List appointments with filters.

    - Filter by patient, provider, status, or date range
    - Paginated results
    """
    if patient_id:
        appointments, total = await get_appointments_by_patient(
            db=db,
            patient_id=patient_id,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    else:
        appointments, total = await get_appointments_by_clinic(
            db=db,
            clinic_id=current_user.clinic_id,
            provider_id=provider_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=pagination.skip,
            limit=pagination.limit,
        )

    return AppointmentListResponse(
        items=appointments,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/calendar", response_model=CalendarViewResponse)
async def get_calendar(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    start: datetime = Query(..., description="Start date for calendar view"),
    end: datetime = Query(..., description="End date for calendar view"),
    provider_id: UUID | None = Query(None),
) -> Any:
    """
    Get calendar view of appointments.

    - Returns all appointments in date range
    - Organized by date
    - Includes availability information
    """
    events = await get_calendar_view(
        db=db,
        clinic_id=current_user.clinic_id,
        provider_id=provider_id,
        start=start,
        end=end,
    )

    return CalendarViewResponse(
        start=start,
        end=end,
        events=events,
    )


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    provider_id: UUID = Query(..., description="Provider ID"),
    date: datetime = Query(..., description="Date to check availability for"),
) -> Any:
    """
    Get provider availability for a specific date.

    - Returns available time slots
    - Considers existing appointments
    - Respects provider working hours
    """
    available_slots = await get_provider_availability(
        db=db,
        provider_id=provider_id,
        date=date,
    )

    return AvailabilityResponse(
        provider_id=str(provider_id),
        date=date.date(),
        available_slots=available_slots,
    )


@router.post("/slots", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_availability_slot(
    data: SlotCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create available time slots for a provider.

    - Used to define when a provider can see patients
    - Can be recurring
    """
    slots = await create_available_slot(
        db=db,
        provider_id=data.provider_id,
        start_time=data.start_time,
        end_time=data.end_time,
        recurring=data.recurring,
    )

    return AvailabilityResponse(
        provider_id=str(data.provider_id),
        date=data.start_time.date(),
        available_slots=slots,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get appointment details.
    """
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    # Verify access
    if appointment.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: UUID,
    data: AppointmentUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Update appointment details.

    - Can reschedule
    - Can change provider
    - Can change appointment type
    """
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if appointment.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Check for new conflicts if rescheduling
    if data.start_time or data.end_time:
        new_start = data.start_time or appointment.start_time
        new_end = data.end_time or appointment.end_time
        new_provider = data.provider_id or appointment.provider_id

        has_conflict = await check_appointment_conflicts(
            db=db,
            provider_id=new_provider,
            start_time=new_start,
            end_time=new_end,
            exclude_appointment_id=appointment_id,
        )

        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New time slot conflicts with existing appointment",
            )

    updated = await update_appointment(db, appointment_id, data)

    # Log modification
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="appointment",
        resource_id=appointment_id,
        action="update",
    )

    return updated


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment_endpoint(
    appointment_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Cancel an appointment.

    - Marks as cancelled
    - Frees up the time slot
    - Sends cancellation notification
    """
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if appointment.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    cancelled = await cancel_appointment(db, appointment_id)

    # Log cancellation
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="appointment",
        resource_id=appointment_id,
        action="cancel",
    )

    return cancelled


@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Confirm a pending appointment.

    - Changes status from 'pending' to 'confirmed'
    - May trigger reminder scheduling
    """
    from app.schemas.appointment import AppointmentUpdate

    return await update_appointment(
        db=db,
        appointment_id=appointment_id,
        data=AppointmentUpdate(status="confirmed"),
    )


@router.post("/{appointment_id}/no-show")
async def mark_no_show(
    appointment_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Mark appointment as no-show.

    - Records that patient did not attend
    - Updates patient no-show count
    """
    from app.schemas.appointment import AppointmentUpdate

    updated = await update_appointment(
        db=db,
        appointment_id=appointment_id,
        data=AppointmentUpdate(status="no_show"),
    )

    # Update patient no-show count
    # TODO: Implement patient no-show tracking

    return {"message": "Marked as no-show", "appointment_id": str(appointment_id)}
