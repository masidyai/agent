"""
CodeExecution schemas for Docker-based code execution
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.code_execution import CodeExecutionStatus, CodeExecutionPhase


class CodeExecutionBase(BaseModel):
    """Base code execution schema"""
    language: Optional[str] = Field(None, max_length=50)
    command: Optional[str] = None


class CodeExecutionCreate(CodeExecutionBase):
    """Schema for creating a code execution"""
    pass


class CodeExecutionUpdate(BaseModel):
    """Schema for updating a code execution"""
    status: Optional[CodeExecutionStatus] = None
    current_phase: Optional[CodeExecutionPhase] = None
    build_output: Optional[str] = None
    test_output: Optional[str] = None
    execution_output: Optional[str] = None


class CodeExecutionResponse(CodeExecutionBase):
    """Schema for code execution response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    status: CodeExecutionStatus
    current_phase: Optional[CodeExecutionPhase] = None
    
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


class CodeExecutionListResponse(BaseModel):
    """Schema for list of code executions"""
    executions: list[CodeExecutionResponse]
    total: int
    page: int
    per_page: int


class CodeExecutionRunRequest(BaseModel):
    """Request to run a code execution"""
    language: Optional[str] = Field(None, description="Programming language (python, javascript, etc.)")
    timeout: int = Field(default=300, ge=10, le=600, description="Timeout in seconds")


class CodeExecutionLogResponse(BaseModel):
    """Response for code execution logs"""
    execution_id: UUID
    logs: str
    timestamp: datetime


class CodeExecutionHealthResponse(BaseModel):
    """Response for code execution health check"""
    execution_id: UUID
    status: CodeExecutionStatus
    is_running: bool
    uptime_seconds: Optional[int] = None
