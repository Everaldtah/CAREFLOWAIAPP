"""
Clinical Encounter Endpoints

Handles patient encounters (visits) and encounter management.
"""

from datetime import datetime
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_provider, Pagination
from app.schemas.encounter import (
    EncounterCreate,
    EncounterUpdate,
    EncounterResponse,
    EncounterListResponse,
)
from app.services.encounter import (
    create_encounter,
    get_encounter_by_id,
    get_patient_encounters,
    get_provider_encounters,
    update_encounter,
    complete_encounter,
)
from app.services.audit import log_phi_access

router = APIRouter()


@router.post("/", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter_endpoint(
    data: EncounterCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new clinical encounter.

    - Records patient visit
    - Links to appointment if applicable
    - Initializes encounter for documentation
    """
    encounter = await create_encounter(
        db=db,
        patient_id=data.patient_id,
        provider_id=data.provider_id or current_user.id,
        clinic_id=current_user.clinic_id,
        appointment_id=data.appointment_id,
        encounter_type=data.encounter_type,
        chief_complaint=data.chief_complaint,
    )

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="encounter",
        resource_id=encounter.id,
        action="create",
    )

    return encounter


@router.get("/", response_model=EncounterListResponse)
async def list_encounters(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
    patient_id: UUID | None = Query(None),
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> Any:
    """
    List encounters with filters.

    - Filter by patient, status, or date range
    - Providers see their encounters
    - Staff can see all clinic encounters
    """
    if patient_id:
        encounters, total = await get_patient_encounters(
            db=db,
            patient_id=patient_id,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    else:
        encounters, total = await get_provider_encounters(
            db=db,
            provider_id=current_user.id,
            clinic_id=current_user.clinic_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=pagination.skip,
            limit=pagination.limit,
        )

    return EncounterListResponse(
        items=encounters,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get encounter details.
    """
    encounter = await get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )

    # Verify access
    if encounter.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return encounter


@router.patch("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter_endpoint(
    encounter_id: UUID,
    data: EncounterUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Update encounter details.

    - Can update chief complaint, status, etc.
    - Logs PHI modifications
    """
    encounter = await get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )

    if encounter.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    updated = await update_encounter(db, encounter_id, data)

    # Log PHI modification
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="encounter",
        resource_id=encounter_id,
        action="update",
    )

    return updated


@router.post("/{encounter_id}/complete", response_model=EncounterResponse)
async def complete_encounter_endpoint(
    encounter_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Mark encounter as complete.

    - Changes status to completed
    - Records end time
    - May trigger billing workflows
    """
    encounter = await get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )

    completed = await complete_encounter(db, encounter_id)

    # Log completion
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="encounter",
        resource_id=encounter_id,
        action="complete",
    )

    return completed
