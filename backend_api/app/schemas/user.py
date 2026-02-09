"""
User schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    is_verified: bool
    oauth_provider: Optional[str] = None
    github_username: Optional[str] = None
    github_account_linked: bool = False
    github_public_repos_count: int = 0
    created_at: datetime


class UserInDB(UserResponse):
    """Schema for user in database"""
    password_hash: Optional[str] = None
    oauth_id: Optional[str] = None
    github_token: Optional[str] = None  # Encrypted
    github_token_expires_at: Optional[datetime] = None
    updated_at: datetime


class UserListResponse(BaseModel):
    """Schema for list of users"""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
