"""
ProjectFile schemas
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectFileBase(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=500)
    content: str
    language: Optional[str] = None


class ProjectFileCreate(ProjectFileBase):
    pass


class ProjectFileUpdate(BaseModel):
    content: Optional[str] = None
    language: Optional[str] = None


class ProjectFileResponse(ProjectFileBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectFileListResponse(BaseModel):
    files: List[ProjectFileResponse]
    total: int
