"""
Authentication Endpoints

Handles user registration, login, token refresh, and logout.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import (
    ActiveUser,
    VerifiedUser,
    get_current_tenant,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
    validate_password_strength,
)
from app.models.user import User, Role
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    EmailVerifyRequest,
)
from app.services.auth import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_user_email,
    initiate_password_reset,
    complete_password_reset,
    revoke_refresh_token,
    save_refresh_token,
)
from app.services.email import send_verification_email, send_password_reset_email

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Register a new user.

    - Requires email, password, and name
    - Password must meet strength requirements
    - Sends verification email
    - Creates default tenant and clinic for first user
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password strength
    is_valid, errors = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors},
        )

    # Create user
    user = await create_user(
        db=db,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        role=Role.PROVIDER if data.is_provider else Role.PATIENT,
        phone=data.phone,
    )

    # Send verification email
    if settings.is_development or settings.app_env == "staging":
        await send_verification_email(user)

    return RegisterResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        is_verified=user.is_verified,
        message="Registration successful. Please check your email to verify your account.",
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Authenticate user and return tokens.

    - Validates email and password
    - Returns access and refresh tokens
    - Includes user information
    """
    # Get user by email
    user = await get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "email": user.email,
            "role": user.role.value,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        },
    )

    refresh_token = create_refresh_token(subject=str(user.id))

    # Store refresh token hash
    await save_refresh_token(db, user.id, refresh_token)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "clinic_id": str(user.clinic_id) if user.clinic_id else None,
        },
    )


@router.post("/token/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Refresh access token using refresh token.

    - Validates refresh token
    - Returns new access token
    - Optionally returns new refresh token
    """
    try:
        payload = verify_refresh_token(data.refresh_token)
        user_id = payload.get("sub")
        jti = payload.get("jti")

        # Get user
        user = await get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Check if token is revoked (you'd implement this check)
        # if await is_token_revoked(db, user_id, jti):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Token has been revoked",
        #     )

        # Create new access token
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role.value,
                "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            },
        )

        # Optionally create new refresh token (rotation)
        new_refresh_token = create_refresh_token(subject=str(user.id))
        await revoke_refresh_token(db, user_id, data.refresh_token)
        await save_refresh_token(db, user.id, new_refresh_token)

        return TokenRefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Logout user by revoking refresh token.

    - Invalidates the refresh token
    - Token cannot be used again
    """
    await revoke_refresh_token(db, current_user.id, refresh_token)
    return {"message": "Successfully logged out"}


@router.post("/verify-email")
async def verify_email(
    data: EmailVerifyRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Verify user email address.

    - Validates verification token
    - Marks user as verified
    """
    success = await verify_user_email(db, data.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Resend email verification.

    - Sends new verification email
    - Only works if not already verified
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    await send_verification_email(current_user)
    return {"message": "Verification email sent"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Initiate password reset.

    - Sends password reset email
    - Always returns success (prevents email enumeration)
    """
    user = await get_user_by_email(db, data.email)
    if user:
        await send_password_reset_email(user)

    return {
        "message": "If an account exists with this email, "
        "a password reset link will be sent"
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Complete password reset.

    - Validates reset token
    - Updates password
    """
    # Validate password strength
    is_valid, errors = validate_password_strength(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors},
        )

    success = await complete_password_reset(
        db=db,
        token=data.token,
        new_password=data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: VerifiedUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Change password for authenticated user.

    - Requires current password
    - Validates new password strength
    - Updates password
    """
    # Verify current password
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Validate new password
    is_valid, errors = validate_password_strength(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors},
        )

    # Update password
    from app.services.user import update_user_password

    await update_user_password(db, current_user.id, data.new_password)

    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: ActiveUser,
) -> Any:
    """
    Get current user information.

    - Returns authenticated user details
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
        "tenant_id": str(current_user.tenant_id) if current_user.tenant_id else None,
        "clinic_id": str(current_user.clinic_id) if current_user.clinic_id else None,
    }
