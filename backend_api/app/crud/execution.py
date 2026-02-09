"""
Execution CRUD operations
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.execution import Execution, ExecutionStep, ExecutionStatus, StepStatus
from app.schemas.execution import (
    ExecutionCreate,
    ExecutionUpdate,
    ExecutionStepCreate,
    ExecutionStepUpdate,
)


class CRUDExecution(CRUDBase[Execution, ExecutionCreate, ExecutionUpdate]):
    """CRUD operations for Execution model"""
    
    async def create_with_project(
        self,
        db: AsyncSession,
        *,
        obj_in: ExecutionCreate,
        project_id: UUID,
    ) -> Execution:
        """Create a new execution for a project"""
        db_obj = Execution(
            project_id=project_id,
            prompt=obj_in.prompt,
            plan=obj_in.plan,
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
    ) -> List[Execution]:
        """Get executions for a project"""
        result = await db.execute(
            select(Execution)
            .options(selectinload(Execution.steps))
            .where(Execution.project_id == project_id)
            .order_by(Execution.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_steps(
        self,
        db: AsyncSession,
        *,
        id: UUID,
    ) -> Optional[Execution]:
        """Get execution with its steps"""
        result = await db.execute(
            select(Execution)
            .options(selectinload(Execution.steps))
            .where(Execution.id == id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        execution: Execution,
        status: ExecutionStatus,
    ) -> Execution:
        """Update execution status"""
        execution.status = status
        if status == ExecutionStatus.IN_PROGRESS and not execution.started_at:
            execution.started_at = datetime.utcnow()
        elif status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.STOPPED]:
            execution.completed_at = datetime.utcnow()
        
        db.add(execution)
        await db.flush()
        await db.refresh(execution)
        return execution
    
    async def count_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> int:
        """Count executions for a project"""
        result = await db.execute(
            select(func.count())
            .select_from(Execution)
            .where(Execution.project_id == project_id)
        )
        return result.scalar() or 0


class CRUDExecutionStep(CRUDBase[ExecutionStep, ExecutionStepCreate, ExecutionStepUpdate]):
    """CRUD operations for ExecutionStep model"""
    
    async def create_with_execution(
        self,
        db: AsyncSession,
        *,
        obj_in: ExecutionStepCreate,
        execution_id: UUID,
    ) -> ExecutionStep:
        """Create a new step for an execution"""
        db_obj = ExecutionStep(
            execution_id=execution_id,
            step_number=obj_in.step_number,
            name=obj_in.name,
            description=obj_in.description,
            tool_name=obj_in.tool_name,
            status=StepStatus.PENDING,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_execution(
        self,
        db: AsyncSession,
        *,
        execution_id: UUID,
    ) -> List[ExecutionStep]:
        """Get steps for an execution"""
        result = await db.execute(
            select(ExecutionStep)
            .where(ExecutionStep.execution_id == execution_id)
            .order_by(ExecutionStep.step_number)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        step: ExecutionStep,
        status: StepStatus,
        output: Optional[str] = None,
        logs: Optional[str] = None,
    ) -> ExecutionStep:
        """Update step status and optionally output/logs"""
        step.status = status
        if output is not None:
            step.output = output
        if logs is not None:
            step.logs = logs
        
        db.add(step)
        await db.flush()
        await db.refresh(step)
        return step


execution = CRUDExecution(Execution)
execution_step = CRUDExecutionStep(ExecutionStep)
