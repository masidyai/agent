"""
Deployment schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.deployment import DeploymentEnvironment, DeploymentStatus, DeploymentProvider


class DeploymentBase(BaseModel):
    """Base deployment schema"""
    environment: DeploymentEnvironment = DeploymentEnvironment.DEV
    provider: DeploymentProvider = DeploymentProvider.VERCEL


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment"""
    project_id: UUID
    branch: str = "main"


class DeploymentUpdate(BaseModel):
    """Schema for updating a deployment"""
    status: Optional[DeploymentStatus] = None
    url: Optional[str] = None
    preview_url: Optional[str] = None
    build_logs: Optional[str] = None
    deploy_logs: Optional[str] = None
    error_message: Optional[str] = None


class DeploymentResponse(DeploymentBase):
    """Schema for deployment response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    status: DeploymentStatus
    url: Optional[str] = None
    preview_url: Optional[str] = None
    error_message: Optional[str] = None
    branch: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class DeploymentWithLogs(DeploymentResponse):
    """Schema for deployment with logs"""
    build_logs: Optional[str] = None
    deploy_logs: Optional[str] = None


class DeploymentListResponse(BaseModel):
    """Schema for list of deployments"""
    deployments: list[DeploymentResponse]
    total: int


class DeploymentTriggerRequest(BaseModel):
    """Schema for triggering a deployment"""
    environment: DeploymentEnvironment = DeploymentEnvironment.DEV
    provider: DeploymentProvider = DeploymentProvider.VERCEL
    branch: str = "main"


class DeploymentTriggerResponse(BaseModel):
    """Schema for deployment trigger response"""
    deployment_id: UUID
    status: str
    message: str
