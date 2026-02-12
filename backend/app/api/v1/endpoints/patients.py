"""
Patient Management Endpoints

CRUD operations for patient records.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_provider, Pagination
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    PatientSearchResponse,
)
from app.services.patient import (
    create_patient,
    get_patient_by_id,
    get_patients_by_clinic,
    update_patient,
    delete_patient,
    search_patients,
    get_patient_timeline,
)
from app.services.audit import log_phi_access

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient_record(
    data: PatientCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new patient record.

    - Requires authentication
    - Creates patient in current user's clinic
    - Logs PHI access
    """
    patient = await create_patient(
        db=db,
        clinic_id=current_user.clinic_id,
        data=data,
    )

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=patient.id,
        action="create",
    )

    return patient


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
    status: str | None = Query(None, description="Filter by status"),
) -> Any:
    """
    List all patients in the clinic.

    - Paginated results
    - Optional status filter
    - Only returns patients from user's clinic
    """
    patients, total = await get_patients_by_clinic(
        db=db,
        clinic_id=current_user.clinic_id,
        skip=pagination.skip,
        limit=pagination.limit,
        status_filter=status,
    )

    return PatientListResponse(
        items=patients,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/search", response_model=List[PatientSearchResponse])
async def search_patient_records(
    query: str = Query(..., min_length=2, description="Search query"),
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Search for patients by name, email, phone, or MRN.

    - Fuzzy search across multiple fields
    - Returns top 20 matches
    """
    results = await search_patients(
        db=db,
        clinic_id=current_user.clinic_id,
        query=query,
        limit=20,
    )

    # Log search (no PHI details, just search action)
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=None,
        action="search",
        details={"query": query},
    )

    return results


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get patient details by ID.

    - Includes all demographic and contact information
    - Logs PHI access
    """
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Verify access to patient's clinic
    if patient.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this patient record",
        )

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=patient.id,
        action="read",
    )

    return patient


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(
    patient_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get patient timeline including appointments, encounters, and notes.

    - Returns chronological patient history
    - Useful for care coordination
    """
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if patient.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    timeline = await get_patient_timeline(db, patient_id)

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=patient_id,
        action="read_timeline",
    )

    return {
        "patient_id": str(patient_id),
        "timeline": timeline,
    }


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient_record(
    patient_id: UUID,
    data: PatientUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Update patient information.

    - Only updates provided fields
    - Logs PHI modification
    """
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if patient.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    updated_patient = await update_patient(db, patient_id, data)

    # Log PHI modification
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=patient_id,
        action="update",
    )

    return updated_patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient_record(
    patient_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """
    Delete (soft delete) a patient record.

    - Marks record as deleted
    - Data remains in database for compliance
    - Cannot be undone by normal users
    """
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if patient.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    await delete_patient(db, patient_id)

    # Log deletion
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="patient",
        resource_id=patient_id,
        action="delete",
    )
