"""
Email Service

Handles sending emails for verification, notifications, etc.
"""

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_verification_email(user) -> bool:
    """Send email verification email."""
    if settings.is_development:
        logger.info(f"[DEV] Verification email would be sent to {user.email}")
        return True

    # In production, use Resend or similar
    try:
        # Send actual email
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


async def send_password_reset_email(user, reset_token: str) -> bool:
    """Send password reset email."""
    if settings.is_development:
        logger.info(f"[DEV] Password reset email would be sent to {user.email}")
        return True

    return True


async def send_appointment_confirmation(appointment, patient) -> bool:
    """Send appointment confirmation email."""
    if settings.is_development:
        logger.info(f"[DEV] Appointment confirmation would be sent to {patient.email}")
        return True

    return True


async def send_appointment_reminder(appointment, patient) -> bool:
    """Send appointment reminder email."""
    if settings.is_development:
        logger.info(f"[DEV] Appointment reminder would be sent to {patient.email}")
        return True

    return True
