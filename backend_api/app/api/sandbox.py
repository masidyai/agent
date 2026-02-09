"""
Sandbox execution API endpoints
"""
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.models.user import User
from app.services.sandbox import sandbox, SandboxConfig
from app.core.database import get_db
from app.services.usage_tracking import usage_tracking

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


class ExecuteCommandRequest(BaseModel):
    """Request to execute a shell command"""
    command: str = Field(..., description="Command to execute")
    timeout: int = Field(default=30, ge=1, le=300)
    project_id: Optional[str] = None


class ExecuteCodeRequest(BaseModel):
    """Request to execute code"""
    code: str = Field(..., description="Source code to execute")
    language: str = Field(..., description="Programming language")
    timeout: int = Field(default=30, ge=1, le=300)
    project_id: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Response from execution"""
    status: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    error: Optional[str] = None


@router.post("/execute", response_model=ExecutionResponse)
async def execute_command(
    request: ExecuteCommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a command in a sandboxed environment.
    
    Allowed commands: node, npm, npx, python, python3, pip, bun, deno, go, rustc, cargo
    """
    # Check quota before execution
    has_quota, message = await usage_tracking.check_quota(
        db, user_id=current_user.id, quota_type="executions"
    )
    if not has_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
        )
    
    config = SandboxConfig(
        timeout_seconds=request.timeout
    )
    
    # Track start time
    start_time = time.time()
    
    result = await sandbox.execute(
        command=request.command,
        config=config,
        project_id=request.project_id
    )
    
    # Calculate duration and log usage
    duration_minutes = (time.time() - start_time) / 60
    await usage_tracking.log_docker_usage(
        db,
        user_id=current_user.id,
        minutes=duration_minutes,
        metadata={
            "command": request.command,
            "project_id": request.project_id,
            "exit_code": result.exit_code,
        },
    )
    
    return ExecutionResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        error=result.error
    )


@router.post("/execute-code", response_model=ExecutionResponse)
async def execute_code(
    request: ExecuteCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute source code in a specific language.
    
    Supported languages: python, javascript, typescript, go, rust
    """
    # Check quota before execution
    has_quota, message = await usage_tracking.check_quota(
        db, user_id=current_user.id, quota_type="executions"
    )
    if not has_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
        )
    
    config = SandboxConfig(
        timeout_seconds=request.timeout
    )
    
    # Track start time
    start_time = time.time()
    
    result = await sandbox.execute_code(
        code=request.code,
        language=request.language,
        config=config,
        project_id=request.project_id
    )
    
    # Calculate duration and log usage
    duration_minutes = (time.time() - start_time) / 60
    await usage_tracking.log_docker_usage(
        db,
        user_id=current_user.id,
        minutes=duration_minutes,
        metadata={
            "language": request.language,
            "project_id": request.project_id,
            "exit_code": result.exit_code,
        },
    )
    
    return ExecutionResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        error=result.error
    )


class BuildProjectRequest(BaseModel):
    """Request to build a project"""
    project_dir: str
    build_command: str = "npm run build"
    timeout: int = Field(default=300, ge=1, le=600)


class InstallDepsRequest(BaseModel):
    """Request to install dependencies"""
    project_dir: str
    package_manager: str = "npm"
    timeout: int = Field(default=120, ge=1, le=300)


class RunTestsRequest(BaseModel):
    """Request to run tests"""
    project_dir: str
    test_command: str = "npm test"
    timeout: int = Field(default=180, ge=1, le=300)


@router.post("/build", response_model=ExecutionResponse)
async def build_project(
    request: BuildProjectRequest,
    current_user: User = Depends(get_current_user)
):
    """Build a project"""
    config = SandboxConfig(
        timeout_seconds=request.timeout
    )
    
    result = await sandbox.build_project(
        project_dir=request.project_dir,
        build_command=request.build_command,
        config=config
    )
    
    return ExecutionResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        error=result.error
    )


@router.post("/install", response_model=ExecutionResponse)
async def install_dependencies(
    request: InstallDepsRequest,
    current_user: User = Depends(get_current_user)
):
    """Install project dependencies"""
    config = SandboxConfig(
        timeout_seconds=request.timeout
    )
    
    result = await sandbox.install_dependencies(
        project_dir=request.project_dir,
        package_manager=request.package_manager,
        config=config
    )
    
    return ExecutionResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        error=result.error
    )


@router.post("/test", response_model=ExecutionResponse)
async def run_tests(
    request: RunTestsRequest,
    current_user: User = Depends(get_current_user)
):
    """Run project tests"""
    config = SandboxConfig(
        timeout_seconds=request.timeout
    )
    
    result = await sandbox.run_tests(
        project_dir=request.project_dir,
        test_command=request.test_command,
        config=config
    )
    
    return ExecutionResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        error=result.error
    )
