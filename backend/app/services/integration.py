"""
Integration Service

Handles EHR and third-party system integrations.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import Integration


async def connect_ehr_integration(
    db: AsyncSession,
    clinic_id: UUID,
    provider: str,
    credentials: dict,
    settings: dict = None,
) -> Integration:
    """Connect to an EHR system."""
    integration = Integration(
        clinic_id=clinic_id,
        provider=provider,
        api_endpoint=credentials.get("endpoint"),
        client_id=credentials.get("client_id"),
        settings=settings or {},
        status="active",
    )

    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return integration


async def trigger_ehr_sync(
    db: AsyncSession,
    integration_id: UUID,
    sync_type: str = "full",
) -> dict:
    """Trigger data sync with EHR."""
    # Create sync job
    job_id = integration_id  # Simplified

    return {
        "id": str(job_id),
        "status": "started",
        "sync_type": sync_type,
    }


async def get_integration_status(
    db: AsyncSession,
    integration_id: UUID,
) -> dict:
    """Get integration status."""
    result = await db.execute(
        select(Integration).where(Integration.id == integration_id)
    )
    integration = result.scalar_one_or_none()

    if integration:
        return {
            "id": str(integration.id),
            "provider": integration.provider,
            "status": integration.status,
            "last_sync": integration.last_sync_at.isoformat() if integration.last_sync_at else None,
        }

    return {}


async def process_fhir_webhook(
    db: AsyncSession,
    payload: dict,
) -> dict:
    """Process incoming FHIR webhook from EHR."""
    # Process FHIR resource
    resource_type = payload.get("resourceType")

    return {
        "status": "processed",
        "resource_type": resource_type,
    }
