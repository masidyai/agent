"""
Deployment CRUD operations
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.deployment import Deployment, DeploymentStatus, DeploymentEnvironment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate


class CRUDDeployment(CRUDBase[Deployment, DeploymentCreate, DeploymentUpdate]):
    """CRUD operations for Deployment model"""
    
    async def get_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Deployment]:
        """Get all deployments for a project"""
        result = await db.execute(
            select(Deployment)
            .where(Deployment.project_id == project_id)
            .order_by(Deployment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_active_deployment(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        environment: DeploymentEnvironment = DeploymentEnvironment.PROD,
    ) -> Optional[Deployment]:
        """Get the active deployment for a project environment"""
        result = await db.execute(
            select(Deployment)
            .where(
                Deployment.project_id == project_id,
                Deployment.environment == environment,
                Deployment.status == DeploymentStatus.ACTIVE,
            )
            .order_by(Deployment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_latest_deployment(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> Optional[Deployment]:
        """Get the latest deployment for a project"""
        result = await db.execute(
            select(Deployment)
            .where(Deployment.project_id == project_id)
            .order_by(Deployment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create_deployment(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        environment: DeploymentEnvironment = DeploymentEnvironment.DEV,
        provider: str = "vercel",
        branch: str = "main",
    ) -> Deployment:
        """Create a new deployment"""
        from app.models.deployment import DeploymentProvider
        
        db_obj = Deployment(
            project_id=project_id,
            environment=environment,
            provider=DeploymentProvider(provider),
            branch=branch,
            status=DeploymentStatus.PENDING,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def start_deployment(
        self,
        db: AsyncSession,
        *,
        deployment: Deployment,
    ) -> Deployment:
        """Mark deployment as building"""
        deployment.status = DeploymentStatus.BUILDING
        deployment.started_at = datetime.utcnow()
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment
    
    async def complete_deployment(
        self,
        db: AsyncSession,
        *,
        deployment: Deployment,
        url: str,
        preview_url: Optional[str] = None,
    ) -> Deployment:
        """Mark deployment as active/completed"""
        deployment.status = DeploymentStatus.ACTIVE
        deployment.url = url
        deployment.preview_url = preview_url
        deployment.completed_at = datetime.utcnow()
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment
    
    async def fail_deployment(
        self,
        db: AsyncSession,
        *,
        deployment: Deployment,
        error_message: str,
        build_logs: Optional[str] = None,
    ) -> Deployment:
        """Mark deployment as failed"""
        deployment.status = DeploymentStatus.FAILED
        deployment.error_message = error_message
        deployment.build_logs = build_logs
        deployment.completed_at = datetime.utcnow()
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment
    
    async def stop_deployment(
        self,
        db: AsyncSession,
        *,
        deployment: Deployment,
    ) -> Deployment:
        """Stop a deployment"""
        deployment.status = DeploymentStatus.STOPPED
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment
    
    async def update_logs(
        self,
        db: AsyncSession,
        *,
        deployment: Deployment,
        build_logs: Optional[str] = None,
        deploy_logs: Optional[str] = None,
    ) -> Deployment:
        """Update deployment logs"""
        if build_logs is not None:
            deployment.build_logs = build_logs
        if deploy_logs is not None:
            deployment.deploy_logs = deploy_logs
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment


deployment = CRUDDeployment(Deployment)
