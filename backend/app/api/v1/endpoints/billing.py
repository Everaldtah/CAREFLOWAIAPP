"""
Billing Endpoints

Handles billing operations, code suggestions, and claims processing.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, Pagination
from app.agents.billing_agent import BillingAgent
from app.services.audit import log_phi_access

router = APIRouter()


class SuggestCodesRequest(BaseModel):
    encounter_id: UUID
    diagnosis_text: str | None = None
    procedure_text: str | None = None
    transcript: str | None = None


class SuggestCodesResponse(BaseModel):
    icd_10_codes: List[dict]
    cpt_codes: List[dict]
    confidence: float
    reasoning: str


@router.post("/suggest-codes", response_model=SuggestCodesResponse)
async def suggest_billing_codes(
    data: SuggestCodesRequest,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Suggest ICD-10 and CPT codes using AI.

    - Analyzes encounter documentation
    - Suggests appropriate diagnosis codes
    - Suggests appropriate procedure codes
    - Includes confidence scores
    """
    billing_agent = BillingAgent(db)

    try:
        suggestions = await billing_agent.suggest_codes(
            encounter_id=data.encounter_id,
            diagnosis_text=data.diagnosis_text,
            procedure_text=data.procedure_text,
            transcript=data.transcript,
        )

        # Log PHI access
        await log_phi_access(
            db=db,
            user_id=current_user.id,
            resource_type="billing",
            resource_id=data.encounter_id,
            action="suggest_codes",
        )

        return SuggestCodesResponse(**suggestions)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code suggestions: {str(e)}",
        )


class ValidateClaimRequest(BaseModel):
    claim_id: UUID


class ValidateClaimResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@router.post("/validate-claim", response_model=ValidateClaimResponse)
async def validate_claim(
    data: ValidateClaimRequest,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Validate an insurance claim before submission.

    - Checks for required fields
    - Validates code combinations
    - Checks for common errors
    """
    billing_agent = BillingAgent(db)

    validation = await billing_agent.validate_claim(
        claim_id=data.claim_id,
    )

    return ValidateClaimResponse(**validation)


@router.post("/create-claim")
async def create_claim_from_encounter(
    encounter_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create an insurance claim from an encounter.

    - Auto-populates from encounter data
    - Includes diagnoses and procedures
    - Creates draft claim for review
    """
    from app.services.billing import create_claim_from_encounter

    claim = await create_claim_from_encounter(
        db=db,
        encounter_id=encounter_id,
        created_by=current_user.id,
    )

    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="claim",
        resource_id=claim.id,
        action="create",
    )

    return claim


@router.get("/revenue-summary")
async def get_revenue_summary(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    start_date: str | None = None,
    end_date: str | None = None,
) -> Any:
    """
    Get revenue summary for the clinic.

    - Total charges
    - Total payments
    - Outstanding balance
    - Claims by status
    """
    from app.services.billing import get_revenue_summary

    summary = await get_revenue_summary(
        db=db,
        clinic_id=current_user.clinic_id,
        start_date=start_date,
        end_date=end_date,
    )

    return summary
