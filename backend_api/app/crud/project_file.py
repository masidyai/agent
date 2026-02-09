"""
ProjectFile CRUD operations
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.project_file import ProjectFile
from app.schemas.project_file import ProjectFileCreate, ProjectFileUpdate


class CRUDProjectFile(CRUDBase[ProjectFile, ProjectFileCreate, ProjectFileUpdate]):
    """CRUD operations for ProjectFile model"""
    
    async def create_with_project(
        self,
        db: AsyncSession,
        *,
        obj_in: ProjectFileCreate,
        project_id: UUID,
    ) -> ProjectFile:
        """Create a new file for a project"""
        db_obj = ProjectFile(
            project_id=project_id,
            file_path=obj_in.file_path,
            content=obj_in.content,
            language=obj_in.language,
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
    ) -> List[ProjectFile]:
        """Get all files for a project"""
        result = await db.execute(
            select(ProjectFile)
            .where(ProjectFile.project_id == project_id)
            .order_by(ProjectFile.file_path)
        )
        return list(result.scalars().all())
    
    async def get_by_path(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        file_path: str,
    ) -> Optional[ProjectFile]:
        """Get a specific file by path"""
        result = await db.execute(
            select(ProjectFile)
            .where(
                ProjectFile.project_id == project_id,
                ProjectFile.file_path == file_path,
            )
        )
        return result.scalar_one_or_none()
    
    async def count_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> int:
        """Count files for a project"""
        result = await db.execute(
            select(func.count())
            .select_from(ProjectFile)
            .where(ProjectFile.project_id == project_id)
        )
        return result.scalar() or 0
    
    async def delete_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
    ) -> int:
        """Delete all files for a project"""
        result = await db.execute(
            select(ProjectFile)
            .where(ProjectFile.project_id == project_id)
        )
        files = result.scalars().all()
        
        for file in files:
            await db.delete(file)
        
        await db.flush()
        return len(files)


project_file = CRUDProjectFile(ProjectFile)
