"""
Execution CRUD operations
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.execution import Execution, ExecutionStatus, ExecutionPhase
from app.schemas.execution import ExecutionCreate, ExecutionUpdate


class CRUDExecution(CRUDBase[Execution, ExecutionCreate, ExecutionUpdate]):
    """CRUD operations for Execution model"""
    
    async def create_for_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        obj_in: ExecutionCreate,
    ) -> Execution:
        """Create a new execution for a project"""
        db_obj = Execution(
            project_id=project_id,
            language=obj_in.language,
            command=obj_in.command,
            status=ExecutionStatus.PENDING,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ExecutionStatus] = None,
    ) -> List[Execution]:
        """Get executions for a project"""
        query = select(Execution).where(Execution.project_id == project_id)
        
        if status:
            query = query.where(Execution.status == status)
        
        query = query.order_by(desc(Execution.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> Optional[Execution]:
        """Get the latest execution for a project"""
        query = (
            select(Execution)
            .where(Execution.project_id == project_id)
            .order_by(desc(Execution.created_at))
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_running_executions(
        self,
        db: AsyncSession,
    ) -> List[Execution]:
        """Get all currently running executions"""
        query = select(Execution).where(
            Execution.status.in_([
                ExecutionStatus.BUILDING,
                ExecutionStatus.LINTING,
                ExecutionStatus.TESTING,
                ExecutionStatus.RUNNING,
            ])
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> int:
        """Count executions for a project"""
        query = select(func.count()).select_from(Execution).where(
            Execution.project_id == project_id
        )
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        execution: Execution,
        status: ExecutionStatus,
        phase: Optional[ExecutionPhase] = None,
    ) -> Execution:
        """Update execution status and phase"""
        execution.status = status
        if phase:
            execution.current_phase = phase
        execution.updated_at = datetime.utcnow()
        
        # Set timestamps
        if status in [ExecutionStatus.BUILDING, ExecutionStatus.LINTING, 
                      ExecutionStatus.TESTING, ExecutionStatus.RUNNING]:
            if not execution.started_at:
                execution.started_at = datetime.utcnow()
        elif status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, 
                       ExecutionStatus.TIMEOUT, ExecutionStatus.CANCELLED]:
            if not execution.completed_at:
                execution.completed_at = datetime.utcnow()
            
            # Calculate execution time
            if execution.started_at:
                duration = execution.completed_at - execution.started_at
                execution.execution_time_ms = int(duration.total_seconds() * 1000)
        
        await db.flush()
        await db.refresh(execution)
        return execution
    
    async def update_build_phase(
        self,
        db: AsyncSession,
        *,
        execution: Execution,
        status: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Execution:
        """Update build phase information"""
        execution.build_status = status
        if output:
            execution.build_output = output
        if error:
            execution.build_error = error
        execution.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(execution)
        return execution
    
    async def update_test_phase(
        self,
        db: AsyncSession,
        *,
        execution: Execution,
        status: str,
        output: Optional[str] = None,
        passed: Optional[int] = None,
        failed: Optional[int] = None,
        coverage: Optional[float] = None,
    ) -> Execution:
        """Update test phase information"""
        execution.test_status = status
        if output:
            execution.test_output = output
        if passed is not None:
            execution.tests_passed = passed
        if failed is not None:
            execution.tests_failed = failed
        if coverage is not None:
            execution.test_coverage = coverage
        execution.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(execution)
        return execution
    
    async def update_metrics(
        self,
        db: AsyncSession,
        *,
        execution: Execution,
        memory_mb: Optional[int] = None,
        cpu_percent: Optional[float] = None,
    ) -> Execution:
        """Update performance metrics"""
        if memory_mb is not None:
            execution.memory_used_mb = memory_mb
        if cpu_percent is not None:
            execution.cpu_usage_percent = cpu_percent
        execution.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(execution)
        return execution


# Create a singleton instance
execution = CRUDExecution(Execution)
