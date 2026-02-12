"""
Authentication Schemas

Request/response schemas for authentication endpoints.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    is_provider: bool = False


class RegisterResponse(BaseModel):
    """Response schema for user registration."""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    message: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response schema for user login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict[str, Any]


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response schema for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    """Request schema for password reset initiation."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request schema for completing password reset."""
    token: str
    new_password: str = Field(..., min_length=8)


class EmailVerifyRequest(BaseModel):
    """Request schema for email verification."""
    token: str
