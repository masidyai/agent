"""
Execution schemas
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.execution import ExecutionStatus, StepStatus


# ExecutionStep schemas
class ExecutionStepBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tool_name: Optional[str] = None


class ExecutionStepCreate(ExecutionStepBase):
    step_number: int = Field(..., ge=0)
    

class ExecutionStepUpdate(BaseModel):
    status: Optional[StepStatus] = None
    output: Optional[str] = None
    logs: Optional[str] = None


class ExecutionStepResponse(ExecutionStepBase):
    id: UUID
    execution_id: UUID
    step_number: int
    status: StepStatus
    output: Optional[str] = None
    logs: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Execution schemas
class ExecutionBase(BaseModel):
    prompt: Optional[str] = None
    plan: Optional[str] = None


class ExecutionCreate(ExecutionBase):
    pass


class ExecutionUpdate(BaseModel):
    status: Optional[ExecutionStatus] = None
    plan: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExecutionResponse(ExecutionBase):
    id: UUID
    project_id: UUID
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    steps: List[ExecutionStepResponse] = []

    model_config = {"from_attributes": True}


class ExecutionListResponse(BaseModel):
    executions: List[ExecutionResponse]
    total: int
    page: int = 1
    per_page: int = 20
