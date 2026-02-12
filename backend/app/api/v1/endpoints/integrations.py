"""
Integrations Endpoints

Handles EHR and third-party integrations.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_admin

router = APIRouter()


class IntegrationConfig(BaseModel):
    provider: str  # 'epic', 'cerner', 'athena', etc.
    credentials: dict
    settings: dict | None = None


@router.post("/connect")
async def connect_integration(
    data: IntegrationConfig,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Connect to an EHR system.

    - Validates credentials
    - Sets up FHIR endpoint
    - Stores secure configuration
    """
    from app.services.integration import connect_ehr_integration

    config = await connect_ehr_integration(
        db=db,
        clinic_id=current_user.clinic_id,
        provider=data.provider,
        credentials=data.credentials,
        settings=data.settings,
    )

    return config


@router.post("/{integration_id}/sync")
async def trigger_sync(
    integration_id: UUID,
    sync_type: str = "full",  # 'full', 'patients', 'appointments'
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Trigger data sync with EHR.

    - Imports patients
    - Syncs appointments
    - Pulls clinical data
    """
    from app.services.integration import trigger_ehr_sync

    sync_job = await trigger_ehr_sync(
        db=db,
        integration_id=integration_id,
        sync_type=sync_type,
    )

    return {
        "message": "Sync started",
        "job_id": str(sync_job.id),
    }


@router.get("/{integration_id}/status")
async def get_integration_status(
    integration_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Get integration status and recent sync jobs."""
    from app.services.integration import get_integration_status

    status_info = await get_integration_status(db, integration_id)
    return status_info


@router.post("/webhooks/fhir")
async def fhir_webhook(
    payload: dict,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Handle incoming FHIR webhook from EHR.

    - Processes patient updates
    - Handles appointment changes
    - Receives lab results
    """
    from app.services.integration import process_fhir_webhook

    result = await process_fhir_webhook(db, payload)
    return result
