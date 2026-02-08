"""
Memory schemas
"""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class MemoryBase(BaseModel):
    """Base memory schema"""
    key: str = Field(..., min_length=1, max_length=255)
    value: Optional[Any] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class MemoryCreate(MemoryBase):
    """Schema for creating a memory entry"""
    project_id: UUID
    expires_at: Optional[datetime] = None


class MemoryUpdate(BaseModel):
    """Schema for updating a memory entry"""
    value: Optional[Any] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class MemoryResponse(MemoryBase):
    """Schema for memory response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class MemoryListResponse(BaseModel):
    """Schema for list of memories"""
    memories: list[MemoryResponse]
    total: int


class MemorySearchRequest(BaseModel):
    """Schema for searching memories"""
    query: str
    category: Optional[str] = None
    limit: int = Field(default=10, le=100)


class MemoryBulkCreate(BaseModel):
    """Schema for bulk creating memories"""
    project_id: UUID
    memories: list[MemoryBase]


class MemoryBulkResponse(BaseModel):
    """Schema for bulk operation response"""
    created: int
    failed: int
    errors: list[str] = []
