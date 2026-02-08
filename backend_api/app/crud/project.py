"""
Project CRUD operations
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """CRUD operations for Project model"""
    
    async def create_with_user(
        self,
        db: AsyncSession,
        *,
        obj_in: ProjectCreate,
        user_id: UUID,
    ) -> Project:
        """Create a new project for a user"""
        db_obj = Project(
            name=obj_in.name,
            description=obj_in.description,
            prompt=obj_in.prompt,
            flow=obj_in.flow,
            user_id=user_id,
            team_id=obj_in.team_id,
            status=ProjectStatus.DRAFT,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
    ) -> list[Project]:
        """Get projects owned by a user"""
        query = select(Project).where(Project.user_id == user_id)
        
        if status:
            query = query.where(Project.status == status)
        
        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_team(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get projects belonging to a team"""
        result = await db.execute(
            select(Project)
            .where(Project.team_id == team_id)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_accessible_projects(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        team_ids: list[UUID],
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get all projects accessible by user (owned or team projects)"""
        conditions = [Project.user_id == user_id]
        if team_ids:
            conditions.append(Project.team_id.in_(team_ids))
        
        result = await db.execute(
            select(Project)
            .where(or_(*conditions))
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
    ) -> int:
        """Count projects owned by a user"""
        result = await db.execute(
            select(func.count())
            .select_from(Project)
            .where(Project.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        project: Project,
        status: ProjectStatus,
    ) -> Project:
        """Update project status"""
        project.status = status
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project
    
    async def update_progress(
        self,
        db: AsyncSession,
        *,
        project: Project,
        steps_completed: int,
        steps_total: int,
        files_count: int = 0,
    ) -> Project:
        """Update project build progress"""
        project.steps_completed = str(steps_completed)
        project.steps_total = str(steps_total)
        project.files_count = str(files_count)
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project
    
    async def search(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Search projects by name or description"""
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(Project)
            .where(
                Project.user_id == user_id,
                or_(
                    Project.name.ilike(search_pattern),
                    Project.description.ilike(search_pattern),
                )
            )
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


project = CRUDProject(Project)
