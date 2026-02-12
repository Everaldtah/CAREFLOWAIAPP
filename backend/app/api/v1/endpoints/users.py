"""
User Management Endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_admin, Pagination
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    list_clinic_users,
)

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    data: UserCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Create a new user (admin only)."""
    user = await create_user(
        db=db,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        clinic_id=data.clinic_id or current_user.clinic_id,
        phone=data.phone,
    )
    return user


@router.get("/")
async def list_users(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """List users in the clinic."""
    users, total = await list_clinic_users(
        db=db,
        clinic_id=current_user.clinic_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return {"items": users, "total": total}


@router.get("/{user_id}")
async def get_user_endpoint(
    user_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Get user by ID."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}")
async def update_user_endpoint(
    user_id: UUID,
    data: UserUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Update user."""
    user = await update_user(db, user_id, data)
    return user
