"""
Team schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.team_member import TeamRole


class TeamBase(BaseModel):
    """Base team schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema for creating a team"""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = None


class TeamResponse(TeamBase):
    """Schema for team response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    owner_id: UUID
    created_at: datetime


class TeamWithMembers(TeamResponse):
    """Schema for team with members"""
    members_count: int = 0


# Team Member schemas
class TeamMemberBase(BaseModel):
    """Base team member schema"""
    role: TeamRole = TeamRole.MEMBER


class TeamMemberCreate(TeamMemberBase):
    """Schema for adding a team member"""
    user_id: UUID


class TeamMemberInvite(BaseModel):
    """Schema for inviting a team member by email"""
    email: str
    role: TeamRole = TeamRole.MEMBER


class TeamMemberUpdate(BaseModel):
    """Schema for updating a team member"""
    role: TeamRole


class TeamMemberResponse(TeamMemberBase):
    """Schema for team member response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    team_id: UUID
    user_id: UUID
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None


class TeamListResponse(BaseModel):
    """Schema for list of teams"""
    teams: list[TeamResponse]
    total: int
