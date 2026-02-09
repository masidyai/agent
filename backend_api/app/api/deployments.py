"""
Deployments API routes
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import deployment as crud_deployment
from app.crud import project as crud_project
from app.crud import billing as crud_billing
from app.schemas.deployment import (
    DeploymentResponse,
    DeploymentWithLogs,
    DeploymentListResponse,
    DeploymentTriggerRequest,
    DeploymentTriggerResponse,
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/project/{project_id}", response_model=DeploymentListResponse)
async def list_project_deployments(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all deployments for a project"""
    # Verify project ownership
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    deployments = await crud_deployment.get_by_project(db, project_id=project_id)
    return DeploymentListResponse(deployments=deployments, total=len(deployments))


@router.get("/{deployment_id}", response_model=DeploymentWithLogs)
async def get_deployment(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deployment details with logs"""
    deployment = await crud_deployment.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=deployment.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    return deployment


@router.post("/project/{project_id}", response_model=DeploymentTriggerResponse, status_code=status.HTTP_201_CREATED)
async def trigger_deployment(
    project_id: UUID,
    request: DeploymentTriggerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a new deployment for a project"""
    # Verify project ownership
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    # Check billing limits
    is_ok, current, limit = await crud_billing.check_limit(
        db, user_id=current_user.id, limit_type="deployments"
    )
    if not is_ok:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Deployment limit reached ({current}/{limit}). Upgrade your plan.",
        )
    
    # Create deployment
    deployment = await crud_deployment.create_deployment(
        db,
        project_id=project_id,
        environment=request.environment,
        provider=request.provider.value,
        branch=request.branch,
    )
    
    # Increment billing usage
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
    if billing:
        await crud_billing.increment_usage(db, billing=billing, deployments=1)
    
    # In a real app, this would trigger an async deployment job
    # For now, we just return the deployment record
    
    return DeploymentTriggerResponse(
        deployment_id=deployment.id,
        status="pending",
        message="Deployment queued",
    )


@router.post("/{deployment_id}/stop", response_model=DeploymentResponse)
async def stop_deployment(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop/deactivate a deployment"""
    deployment = await crud_deployment.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=deployment.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    deployment = await crud_deployment.stop_deployment(db, deployment=deployment)
    return deployment


@router.delete("/{deployment_id}")
async def delete_deployment(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a deployment record"""
    deployment = await crud_deployment.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    # Verify project ownership
    project = await crud_project.get(db, id=deployment.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    await crud_deployment.delete(db, id=deployment_id)
    return {"message": "Deployment deleted"}
