"""
Authentication Service

Handles user authentication, registration, and token management.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.core.config import settings


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str,
    phone: Optional[str] = None,
    clinic_id: Optional[UUID] = None,
) -> User:
    """Create a new user."""
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    # Create tenant if this is first user
    if role == "provider":
        # For simplicity, create a new tenant
        tenant = Tenant(
            name=f"{first_name} {last_name} Practice",
            slug=email.split("@")[0].lower(),
            plan="professional",
        )
        db.add(tenant)
        await db.flush()
        tenant_id = tenant.id
    else:
        tenant_id = None

    # Create user
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        phone=phone,
        tenant_id=tenant_id,
        clinic_id=clinic_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    return result.scalar_one_or_none()


async def verify_user_email(db: AsyncSession, token: str) -> bool:
    """Verify user email with token."""
    # Simplified - would use proper token verification
    return True


async def save_refresh_token(
    db: AsyncSession,
    user_id: UUID,
    refresh_token: str,
) -> None:
    """Save refresh token hash."""
    # In production, store in separate refresh_tokens table
    pass


async def revoke_refresh_token(
    db: AsyncSession,
    user_id: UUID,
    refresh_token: str,
) -> None:
    """Revoke a refresh token."""
    # In production, mark as revoked in database
    pass


async def initiate_password_reset(db: AsyncSession, email: str) -> bool:
    """Initiate password reset process."""
    user = await get_user_by_email(db, email)
    if not user:
        return True  # Don't reveal if email exists

    # Generate reset token (simplified)
    reset_token = secrets.token_urlsafe(32)
    # In production, store token and expiry

    return True


async def complete_password_reset(
    db: AsyncSession,
    token: str,
    new_password: str,
) -> bool:
    """Complete password reset with token."""
    # In production, verify token and update password
    return True
