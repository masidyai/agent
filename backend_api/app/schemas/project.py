"""
Project schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectStatus, ProjectFlow


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    prompt: Optional[str] = None
    flow: ProjectFlow = ProjectFlow.SAAS


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    team_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    team_id: Optional[UUID] = None
    status: ProjectStatus
    output_path: Optional[str] = None
    files_count: str = "0"
    steps_completed: str = "0"
    steps_total: str = "0"
    github_repo_url: Optional[str] = None
    github_repo_name: Optional[str] = None
    github_repo_id: Optional[int] = None
    github_created_at: Optional[datetime] = None
    github_last_sync: Optional[datetime] = None
    is_public: bool = False
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Schema for list of projects"""
    projects: list[ProjectResponse]
    total: int
    page: int
    per_page: int


class ProjectExecuteRequest(BaseModel):
    """Schema for executing a project"""
    prompt: str = Field(..., min_length=3)
    flow: ProjectFlow = ProjectFlow.SAAS


class ProjectExecuteResponse(BaseModel):
    """Schema for project execution response"""
    project_id: UUID
    execution_id: str
    status: str
    message: str
