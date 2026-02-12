"""
Insurance Claims Endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, Pagination
from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimResponse
from app.services.claim import (
    create_claim,
    get_claim_by_id,
    get_claims_by_clinic,
    update_claim,
    submit_claim,
    process_claim_remittance,
)

router = APIRouter()


@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim_endpoint(
    data: ClaimCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Create a new insurance claim."""
    claim = await create_claim(
        db=db,
        encounter_id=data.encounter_id,
        created_by=current_user.id,
        insurance_id=data.insurance_id,
    )
    return claim


@router.get("/")
async def list_claims(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """List claims for the clinic."""
    claims, total = await get_claims_by_clinic(
        db=db,
        clinic_id=current_user.clinic_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return {"items": claims, "total": total}


@router.post("/{claim_id}/submit")
async def submit_claim_endpoint(
    claim_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Submit claim to insurance payer."""
    claim = await submit_claim(db, claim_id)
    return claim
