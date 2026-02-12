"""
Audit Service

HIPAA-compliant audit logging for PHI access.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog, AuditAction

logger = logging.getLogger(__name__)


async def log_phi_access(
    db: AsyncSession,
    user_id: UUID,
    resource_type: str,
    resource_id: Optional[UUID],
    action: str,
    details: Optional[dict] = None,
) -> AuditLog:
    """
    Log PHI access for HIPAA compliance.

    Args:
        db: Database session
        user_id: User who accessed the resource
        resource_type: Type of resource (patient, note, etc.)
        resource_id: ID of the resource
        action: Action performed (read, write, delete, etc.)
        details: Additional details

    Returns:
        Created audit log entry
    """
    log_entry = AuditLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        details=details,
    )

    db.add(log_entry)
    await db.commit()

    logger.info(f"PHI access logged: {action} on {resource_type}:{resource_id} by user:{user_id}")

    return log_entry


async def log_access_denied(
    db: AsyncSession,
    user_id: Optional[UUID],
    resource_type: str,
    resource_id: Optional[UUID],
    reason: str,
) -> AuditLog:
    """Log denied access attempt."""
    log_entry = AuditLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=AuditAction.ACCESS_DENIED,
        success=False,
        error_message=reason,
    )

    db.add(log_entry)
    await db.commit()

    logger.warning(f"Access denied: {resource_type}:{resource_id} - {reason}")

    return log_entry
