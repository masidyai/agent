"""
Execution API endpoints for running and monitoring code execution
"""
import logging
import os
from uuid import UUID
from typing import Optional
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import code_execution as crud_code_execution
from app.crud import project as crud_project
from app.crud import billing as crud_billing
from app.schemas.code_execution import (
    CodeExecutionCreate,
    CodeExecutionResponse,
    CodeExecutionListResponse,
    CodeExecutionRunRequest,
    CodeExecutionLogResponse,
    CodeExecutionHealthResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.code_execution import CodeExecutionStatus, CodeExecutionPhase
from app.services.docker_executor import docker_executor, DockerExecutionConfig

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=CodeExecutionListResponse)
async def list_executions(
    project_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List executions, optionally filtered by project"""
    if project_id:
        # Verify project ownership
        project = await crud_project.get(db, id=project_id)
        if not project or project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        executions = await crud_code_execution.get_by_project(
            db, project_id=project_id, skip=skip, limit=limit
        )
        total = await crud_code_execution.count_by_project(db, project_id=project_id)
    else:
        # Get all executions for user's projects (would need to join with projects)
        # For now, require project_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_id parameter is required"
        )
    
    return CodeExecutionListResponse(
        executions=executions,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("/", response_model=CodeExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    project_id: UUID,
    execution_in: CodeExecutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new execution for a project"""
    # Verify project exists and user owns it
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create execution for this project"
        )
    
    # Check billing limits
    is_ok, current, limit = await crud_billing.check_limit(
        db, user_id=current_user.id, limit_type="executions"
    )
    if not is_ok:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Execution limit reached ({current}/{limit}). Upgrade your plan.",
        )
    
    # Create execution
    execution = await crud_code_execution.create_for_project(
        db, project_id=project_id, obj_in=execution_in
    )
    
    # Increment billing usage
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
    if billing:
        await crud_billing.increment_usage(db, billing=billing, executions=1)
    
    await db.commit()
    
    return execution


@router.get("/{execution_id}", response_model=CodeExecutionResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get execution details"""
    execution = await crud_code_execution.get(db, id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this execution"
        )
    
    return execution


@router.post("/{execution_id}/run", response_model=CodeExecutionResponse)
async def run_execution(
    execution_id: UUID,
    request: CodeExecutionRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start running an execution"""
    execution = await crud_code_execution.get(db, id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to run this execution"
        )
    
    # Check if already running
    if execution.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execution is already running"
        )
    
    # Check if Docker is available
    if not docker_executor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker execution service not available"
        )
    
    # Verify project output path exists
    if not project.output_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has no output path configured"
        )
    
    # Update execution status to running
    execution = await crud_code_execution.update_status(
        db, execution=execution, status=CodeExecutionStatus.BUILDING, phase=CodeExecutionPhase.BUILD
    )
    await db.commit()
    
    # Run execution in background
    background_tasks.add_task(
        _run_execution_task,
        execution_id=execution.id,
        project_path=project.output_path,
        language=request.language or execution.language or "python",
        timeout=request.timeout,
    )
    
    return execution


async def _run_execution_task(
    execution_id: UUID,
    project_path: str,
    language: str,
    timeout: int,
):
    """Background task to run execution"""
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        try:
            execution = await crud_code_execution.get(db, id=execution_id)
            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return
            
            # Configure Docker execution
            config = DockerExecutionConfig(
                language=language,
                timeout_seconds=timeout,
                max_memory_mb=int(os.getenv("MAX_MEMORY", "512")),
                max_cpu_cores=float(os.getenv("MAX_CPU", "1.0")),
                keep_container=os.getenv("KEEP_CONTAINERS", "false").lower() == "true",
            )
            
            # Stream callback to update database
            async def stream_callback(phase: str, message: str):
                logger.info(f"[{execution_id}] [{phase}] {message}")
                # Update current phase in database
                if phase == "build":
                    await crud_code_execution.update_status(
                        db, execution=execution, 
                        status=CodeExecutionStatus.BUILDING, 
                        phase=CodeExecutionPhase.BUILD
                    )
                elif phase == "lint":
                    await crud_code_execution.update_status(
                        db, execution=execution,
                        status=CodeExecutionStatus.LINTING,
                        phase=CodeExecutionPhase.LINT
                    )
                elif phase == "test":
                    await crud_code_execution.update_status(
                        db, execution=execution,
                        status=CodeExecutionStatus.TESTING,
                        phase=CodeExecutionPhase.TEST
                    )
                elif phase == "execution":
                    await crud_code_execution.update_status(
                        db, execution=execution,
                        status=CodeExecutionStatus.RUNNING,
                        phase=CodeExecutionPhase.EXECUTION
                    )
                await db.commit()
            
            # Run Docker execution
            result = await docker_executor.execute_pipeline(
                project_path=project_path,
                config=config,
                stream_callback=stream_callback,
            )
            
            # Update execution with results
            execution.container_id = result.container_id
            execution.container_image = config.docker_image or docker_executor._get_image_for_language(language)
            
            # Build phase
            execution.build_output = result.build_output
            execution.build_error = result.build_error
            execution.build_status = "passed" if not result.build_error else "failed"
            
            # Lint phase
            execution.lint_output = result.lint_output
            execution.lint_issues = result.lint_issues
            execution.lint_status = "passed" if not result.lint_issues else "warning"
            
            # Test phase
            execution.test_output = result.test_output
            execution.tests_passed = result.tests_passed
            execution.tests_failed = result.tests_failed
            execution.test_coverage = result.test_coverage
            execution.test_status = "passed" if result.tests_failed == 0 else "failed"
            
            # Execution phase
            execution.execution_output = result.output
            execution.execution_error = result.error
            execution.exit_code = result.exit_code
            
            # Metrics
            execution.execution_time_ms = result.duration_ms
            execution.memory_used_mb = result.memory_used_mb
            
            # Final status
            execution = await crud_code_execution.update_status(
                db, execution=execution, status=result.status
            )
            
            await db.commit()
            logger.info(f"Execution {execution_id} completed with status: {result.status}")
            
        except Exception as e:
            logger.error(f"Error running execution {execution_id}: {e}", exc_info=True)
            # Update execution with error
            try:
                execution = await crud_code_execution.get(db, id=execution_id)
                if execution:
                    execution.execution_error = str(e)
                    await crud_code_execution.update_status(
                        db, execution=execution, status=CodeExecutionStatus.FAILED
                    )
                    await db.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update execution error: {inner_e}")


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get execution logs (streaming)"""
    execution = await crud_code_execution.get(db, id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this execution"
        )
    
    # Combine all logs
    logs = []
    
    if execution.build_output:
        logs.append(f"=== BUILD OUTPUT ===\n{execution.build_output}\n")
    if execution.build_error:
        logs.append(f"=== BUILD ERROR ===\n{execution.build_error}\n")
    
    if execution.lint_output:
        logs.append(f"=== LINT OUTPUT ===\n{execution.lint_output}\n")
    
    if execution.test_output:
        logs.append(f"=== TEST OUTPUT ===\n{execution.test_output}\n")
    
    if execution.execution_output:
        logs.append(f"=== EXECUTION OUTPUT ===\n{execution.execution_output}\n")
    if execution.execution_error:
        logs.append(f"=== EXECUTION ERROR ===\n{execution.execution_error}\n")
    
    combined_logs = "\n".join(logs) if logs else "No logs available"
    
    return CodeExecutionLogResponse(
        execution_id=execution.id,
        logs=combined_logs,
        timestamp=execution.updated_at,
    )


@router.get("/{execution_id}/results", response_model=CodeExecutionResponse)
async def get_execution_results(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get execution results (same as get execution, but named endpoint)"""
    return await get_execution(execution_id, db, current_user)


@router.post("/{execution_id}/stop")
async def stop_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a running execution"""
    execution = await crud_code_execution.get(db, id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to stop this execution"
        )
    
    # Check if running
    if not execution.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execution is not running"
        )
    
    # Stop container if exists
    if execution.container_id and docker_executor:
        success = await docker_executor.stop_execution(execution.container_id)
        if not success:
            logger.warning(f"Failed to stop container {execution.container_id}")
    
    # Update status
    execution = await crud_code_execution.update_status(
        db, execution=execution, status=CodeExecutionStatus.CANCELLED
    )
    await db.commit()
    
    return {"message": "Execution stopped successfully"}


@router.get("/{execution_id}/health", response_model=CodeExecutionHealthResponse)
async def get_execution_health(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if execution is still running"""
    execution = await crud_code_execution.get(db, id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this execution"
        )
    
    uptime_seconds = None
    if execution.is_running and execution.started_at:
        from datetime import datetime
        uptime = datetime.utcnow() - execution.started_at
        uptime_seconds = int(uptime.total_seconds())
    
    return CodeExecutionHealthResponse(
        execution_id=execution.id,
        status=execution.status,
        is_running=execution.is_running,
        uptime_seconds=uptime_seconds,
    )
