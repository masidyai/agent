"""
Authentication schemas
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str
    exp: int
    type: str


class LoginRequest(BaseModel):
    """Login request with email and password"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = Field(None, max_length=255)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=6)


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=6)


class OAuthRequest(BaseModel):
    """OAuth authentication request"""
    provider: str  # google, github
    code: str
    redirect_uri: Optional[str] = None
