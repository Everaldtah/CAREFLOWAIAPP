"""
Dependencies Module for CareFlow AI

Provides reusable dependency injection functions for FastAPI routes.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_async_db, get_db
from app.core.security import (
    JWTError,
    verify_access_token,
    verify_refresh_token,
    verify_api_key,
)
from app.models.user import User, Role
from app.models.tenant import Tenant
from app.models.clinic import Clinic
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.encounter import Encounter
from app.models.note import Note
from app.models.conversation import Conversation

# =============================================================================
# Authentication Dependencies
# =============================================================================
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> "User":
    """
    Get the currently authenticated user from access token.

    Args:
        token: HTTP Bearer token
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.models.user import User
    from app.services.user import get_user_by_id

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_access_token(token.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_active_user(
    current_user: Annotated["User", Depends(get_current_user)],
) -> "User":
    """
    Get the currently active user.

    Args:
        current_user: Current user from token

    Returns:
        Active user object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated["User", Depends(get_current_active_user)],
) -> "User":
    """
    Get the currently verified user.

    Args:
        current_user: Current active user

    Returns:
        Verified user object

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user


# =============================================================================
# Role-based Access Control
# =============================================================================
class RoleChecker:
    """Dependency for checking user roles."""

    def __init__(self, allowed_roles: list[str]):
        """
        Initialize role checker.

        Args:
            allowed_roles: List of allowed role names
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated["User", Depends(get_current_user)]) -> "User":
        """
        Check if current user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            User if authorized

        Raises:
            HTTPException: If user lacks required role
        """
        from app.models.user import Role

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        return current_user


# Pre-configured role checkers
require_admin = RoleChecker([Role.ADMIN])
require_provider = RoleChecker([Role.ADMIN, Role.PROVIDER])
require_nurse = RoleChecker([Role.ADMIN, Role.PROVIDER, Role.NURSE])
require_staff = RoleChecker([Role.ADMIN, Role.PROVIDER, Role.NURSE, Role.STAFF])
require_receptionist = RoleChecker([Role.ADMIN, Role.PROVIDER, Role.NURSE, Role.STAFF, Role.RECEPTIONIST])
require_patient = RoleChecker([Role.PATIENT])


# =============================================================================
# Permission Checker
# =============================================================================
class PermissionChecker:
    """Dependency for checking specific permissions."""

    def __init__(self, required_permission: str):
        """
        Initialize permission checker.

        Args:
            required_permission: Permission string required
        """
        self.required_permission = required_permission

    def __call__(
        self,
        current_user: Annotated["User", Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_async_db)],
    ) -> "User":
        """
        Check if current user has required permission.

        Args:
            current_user: Current authenticated user
            db: Database session

        Returns:
            User if authorized

        Raises:
            HTTPException: If user lacks required permission
        """
        from app.services.user import has_permission

        if not has_permission(db, current_user, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.required_permission}",
            )
        return current_user


# =============================================================================
# Tenant Isolation
# =============================================================================
async def get_current_tenant(
    current_user: Annotated["User", Depends(get_current_user)],
) -> "Tenant":
    """
    Get the current tenant from authenticated user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current tenant object

    Raises:
        HTTPException: If tenant not found
    """
    from app.models.tenant import Tenant
    from app.services.tenant import get_tenant_by_id

    tenant = await get_tenant_by_id(current_user.tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is inactive",
        )

    return tenant


async def get_current_clinic(
    current_user: Annotated["User", Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> "Clinic":
    """
    Get the current clinic from authenticated user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Current clinic object

    Raises:
        HTTPException: If clinic not found
    """
    from app.models.clinic import Clinic
    from app.services.clinic import get_clinic_by_id

    if not current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to a clinic",
        )

    clinic = await get_clinic_by_id(db, current_user.clinic_id)
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    return clinic


# =============================================================================
# API Key Authentication
# =============================================================================
async def get_api_key_user(
    x_api_key: Annotated[str, Header()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> "User":
    """
    Authenticate user via API key.

    Args:
        x_api_key: API key from header
        db: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If API key is invalid
    """
    from app.models.user import User
    from app.services.user import get_user_by_api_key

    user = await get_user_by_api_key(db, x_api_key)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# =============================================================================
# Pagination
# =============================================================================
class PaginationParams:
    """Pagination parameters."""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        """
        Initialize pagination parameters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        """
        self.skip = skip
        self.limit = min(limit, 100)  # Cap at 100


async def get_pagination(
    skip: int = 0,
    limit: int = 100,
) -> PaginationParams:
    """
    Get pagination parameters.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Pagination parameters
    """
    return PaginationParams(skip=skip, limit=limit)


# =============================================================================
# Type Aliases
# =============================================================================

"""Current user (any role)"""
CurrentUser = Annotated[User, Depends(get_current_user)]

"""Active user (verified and active)"""
ActiveUser = Annotated[User, Depends(get_current_active_user)]

"""Verified user (email verified)"""
VerifiedUser = Annotated[User, Depends(get_current_verified_user)]

"""Admin user"""
AdminUser = Annotated[User, Depends(require_admin)]

"""Provider user"""
ProviderUser = Annotated[User, Depends(require_provider)]

"""Tenant"""
CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]

"""Clinic"""
CurrentClinic = Annotated[Clinic, Depends(get_current_clinic)]

"""Database session"""
DB = Annotated[AsyncSession, Depends(get_async_db)]

"""Sync database session"""
SyncDB = Annotated[Session, Depends(get_db)]

"""Pagination"""
Pagination = Annotated[PaginationParams, Depends(get_pagination)]
