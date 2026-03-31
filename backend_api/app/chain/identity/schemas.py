"""
Identity and key vault schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class MasidyIdentityBase(BaseModel):
    """Base schema for Masidy Identity"""
    email: EmailStr
    device_fingerprint: Optional[str] = None


class MasidyIdentityCreate(MasidyIdentityBase):
    """Schema for creating a Masidy Identity"""
    pass


class MasidyIdentityResponse(MasidyIdentityBase):
    """Response schema for Masidy Identity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    masidy_id: str
    user_id: UUID
    root_key_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class RootKeyResponse(BaseModel):
    """Response schema for Root Key"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    key_id: str
    masidy_id: str
    status: str
    created_at: datetime
    rotated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


class DerivedKeyCreate(BaseModel):
    """Schema for creating a derived key"""
    scope: str = Field(..., description="Scope of the key (e.g., 'project', 'integration')")
    scope_id: Optional[str] = Field(None, description="ID of the scoped resource")


class DerivedKeyResponse(BaseModel):
    """Response schema for Derived Key"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    key_id: str
    masidy_id: str
    scope: str
    scope_id: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    # Include the actual key value only when needed
    key_value: Optional[str] = None


class CreateIdentityRequest(BaseModel):
    """Request to create a new Masidy Identity"""
    device_fingerprint: Optional[str] = None


class CreateIdentityResponse(BaseModel):
    """Response after creating a Masidy Identity"""
    masidy_id: str
    identity: MasidyIdentityResponse
    root_key: RootKeyResponse


class DeriveKeyRequest(BaseModel):
    """Request to derive a scoped key"""
    masidy_id: str
    scope: str
    scope_id: Optional[str] = None


class DeriveKeyResponse(BaseModel):
    """Response after deriving a key"""
    derived_key: DerivedKeyResponse
