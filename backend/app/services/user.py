"""
User Service

Business logic for user operations.
"""

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash


async def list_clinic_users(
    db: AsyncSession,
    clinic_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[User], int]:
    """List users in a clinic."""
    result = await db.execute(
        select(User)
        .where(User.clinic_id == clinic_id)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(User.id).where(User.clinic_id == clinic_id)
    )
    total = len(count_result.all())

    return list(users), total


async def update_user_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str,
) -> User:
    """Update user password."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)

    return user


async def get_user_by_api_key(
    db: AsyncSession,
    api_key: str,
) -> Optional[User]:
    """Get user by API key."""
    result = await db.execute(
        select(User).where(User.api_key_hash == api_key)
    )
    return result.scalar_one_or_none()


async def has_permission(
    db: AsyncSession,
    user: User,
    permission: str,
) -> bool:
    """Check if user has a specific permission."""
    # Admins have all permissions
    if user.role == "admin":
        return True

    # Check user's permission list
    return permission in user.permissions
