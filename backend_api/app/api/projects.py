"""
Projects API routes
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import project as crud_project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import ProjectStatus
from app.services.usage_tracking import usage_tracking

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    status: ProjectStatus = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's projects"""
    projects = await crud_project.get_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )
    total = await crud_project.count_by_user(db, user_id=current_user.id)
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project"""
    # Check quota before creating project
    has_quota, message = await usage_tracking.check_quota(
        db, user_id=current_user.id, quota_type="projects"
    )
    if not has_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
        )
    
    # If team_id provided, verify membership
    if project_in.team_id:
        from app.crud import team_member as crud_team_member
        member = await crud_team_member.get_by_team_and_user(
            db, team_id=project_in.team_id, user_id=current_user.id
        )
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this team",
            )
    
    project = await crud_project.create_with_user(
        db, obj_in=project_in, user_id=current_user.id
    )
    
    # Log project creation
    await usage_tracking.log_project_creation(
        db,
        user_id=current_user.id,
        project_id=project.id,
        extra_data={"name": project.name, "description": project.description},
    )
    
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details"""
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Check ownership or team membership
    if project.user_id != current_user.id:
        if project.team_id:
            from app.crud import team_member as crud_team_member
            member = await crud_team_member.get_by_team_and_user(
                db, team_id=project.team_id, user_id=current_user.id
            )
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this project",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project",
            )
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project details"""
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project",
        )
    
    project = await crud_project.update(db, db_obj=project, obj_in=project_in)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a project"""
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project",
        )
    
    await crud_project.delete(db, id=project_id)
    return {"message": "Project deleted successfully"}


@router.get("/search/", response_model=ProjectListResponse)
async def search_projects(
    q: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search projects by name or description"""
    projects = await crud_project.search(
        db,
        user_id=current_user.id,
        query=q,
        skip=skip,
        limit=limit,
    )
    
    return ProjectListResponse(
        projects=projects,
        total=len(projects),
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Archive a project"""
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
    
    project = await crud_project.update_status(
        db, project=project, status=ProjectStatus.ARCHIVED
    )
    return project
