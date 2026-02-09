"""
Chain event schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ChainEventBase(BaseModel):
    """Base schema for Chain Event"""
    actor: str
    actor_type: str = Field(..., description="Type of actor: user, system, ai_agent")
    action: str
    target: Optional[str] = None
    target_type: Optional[str] = None
    event_metadata: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ChainEventCreate(ChainEventBase):
    """Schema for creating a Chain Event"""
    pass


class ChainEventResponse(ChainEventBase):
    """Response schema for Chain Event"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    event_id: str
    ai_risk_score: float
    risk_level: str
    event_hash: str
    prev_hash: Optional[str] = None
    timestamp: datetime


class LogEventRequest(BaseModel):
    """Request to log a chain event"""
    action: str
    target: Optional[str] = None
    target_type: Optional[str] = None
    metadata: Optional[dict] = None


class LogEventResponse(BaseModel):
    """Response after logging an event"""
    event: ChainEventResponse
    verified: bool = Field(..., description="Whether event hash chain is valid")
