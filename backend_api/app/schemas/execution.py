"""
Execution schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.execution import ExecutionStatus, ExecutionPhase


class ExecutionBase(BaseModel):
    """Base execution schema"""
    language: Optional[str] = Field(None, max_length=50)
    command: Optional[str] = None


class ExecutionCreate(ExecutionBase):
    """Schema for creating an execution"""
    pass


class ExecutionUpdate(BaseModel):
    """Schema for updating an execution"""
    status: Optional[ExecutionStatus] = None
    current_phase: Optional[ExecutionPhase] = None
    build_output: Optional[str] = None
    test_output: Optional[str] = None
    execution_output: Optional[str] = None


class ExecutionResponse(ExecutionBase):
    """Schema for execution response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    status: ExecutionStatus
    current_phase: Optional[ExecutionPhase] = None
    
    # Build phase
    build_status: Optional[str] = None
    build_output: Optional[str] = None
    build_error: Optional[str] = None
    
    # Lint phase
    lint_status: Optional[str] = None
    lint_output: Optional[str] = None
    lint_issues: Optional[Dict[str, Any]] = None
    
    # Test phase
    test_status: Optional[str] = None
    test_output: Optional[str] = None
    tests_passed: Optional[int] = None
    tests_failed: Optional[int] = None
    test_coverage: Optional[float] = None
    
    # Execution phase
    execution_output: Optional[str] = None
    execution_error: Optional[str] = None
    exit_code: Optional[int] = None
    
    # Validation & errors
    validation_errors: Optional[Dict[str, Any]] = None
    runtime_errors: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    execution_time_ms: Optional[int] = None
    memory_used_mb: Optional[int] = None
    cpu_usage_percent: Optional[float] = None
    
    # Docker container info
    container_id: Optional[str] = None
    container_image: Optional[str] = None
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ExecutionListResponse(BaseModel):
    """Schema for list of executions"""
    executions: list[ExecutionResponse]
    total: int
    page: int
    per_page: int


class ExecutionRunRequest(BaseModel):
    """Request to run an execution"""
    language: Optional[str] = Field(None, description="Programming language (python, javascript, etc.)")
    timeout: int = Field(default=300, ge=10, le=600, description="Timeout in seconds")


class ExecutionLogResponse(BaseModel):
    """Response for execution logs"""
    execution_id: UUID
    logs: str
    timestamp: datetime


class ExecutionHealthResponse(BaseModel):
    """Response for execution health check"""
    execution_id: UUID
    status: ExecutionStatus
    is_running: bool
    uptime_seconds: Optional[int] = None
