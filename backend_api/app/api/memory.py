"""
Memory API routes
"""
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import memory as crud_memory
from app.crud import project as crud_project
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemoryListResponse,
    MemorySearchRequest,
    MemoryBulkCreate,
    MemoryBulkResponse,
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


async def verify_project_access(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
) -> bool:
    """Verify user has access to the project"""
    project = await crud_project.get(db, id=project_id)
    if not project:
        return False
    
    if project.user_id == user_id:
        return True
    
    if project.team_id:
        from app.crud import team_member as crud_team_member
        member = await crud_team_member.get_by_team_and_user(
            db, team_id=project.team_id, user_id=user_id
        )
        return member is not None
    
    return False


@router.get("/project/{project_id}", response_model=MemoryListResponse)
async def list_project_memories(
    project_id: UUID,
    category: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all memories for a project"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    
    memories = await crud_memory.get_by_project(
        db,
        project_id=project_id,
        category=category,
        skip=skip,
        limit=limit,
    )
    return MemoryListResponse(memories=memories, total=len(memories))


@router.get("/project/{project_id}/key/{key}", response_model=MemoryResponse)
async def get_memory_by_key(
    project_id: UUID,
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a memory entry by key"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    memory = await crud_memory.get_by_key(db, project_id=project_id, key=key)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )
    
    return memory


@router.get("/project/{project_id}/value/{key}")
async def get_memory_value(
    project_id: UUID,
    key: str,
    default: Any = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get just the value of a memory entry"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    value = await crud_memory.get_value(db, project_id=project_id, key=key, default=default)
    return {"key": key, "value": value}


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_in: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update a memory entry"""
    if not await verify_project_access(db, memory_in.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    memory = await crud_memory.set_memory(
        db,
        project_id=memory_in.project_id,
        key=memory_in.key,
        value=memory_in.value,
        category=memory_in.category,
        description=memory_in.description,
        expires_at=memory_in.expires_at,
    )
    return memory


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: UUID,
    memory_in: MemoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a memory entry"""
    memory = await crud_memory.get(db, id=memory_id)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )
    
    if not await verify_project_access(db, memory.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    memory = await crud_memory.update(db, db_obj=memory, obj_in=memory_in)
    return memory


@router.delete("/project/{project_id}/key/{key}")
async def delete_memory_by_key(
    project_id: UUID,
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a memory entry by key"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    success = await crud_memory.delete_by_key(db, project_id=project_id, key=key)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )
    
    return {"message": "Memory deleted"}


@router.delete("/project/{project_id}/category/{category}")
async def delete_category(
    project_id: UUID,
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all memories in a category"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    count = await crud_memory.delete_by_category(
        db, project_id=project_id, category=category
    )
    return {"message": f"Deleted {count} memories"}


@router.post("/search", response_model=MemoryListResponse)
async def search_memories(
    project_id: UUID,
    request: MemorySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search memories by key or description"""
    if not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    memories = await crud_memory.search_memories(
        db,
        project_id=project_id,
        query=request.query,
        category=request.category,
        limit=request.limit,
    )
    return MemoryListResponse(memories=memories, total=len(memories))


@router.post("/bulk", response_model=MemoryBulkResponse)
async def bulk_create_memories(
    request: MemoryBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk create/update memories"""
    if not await verify_project_access(db, request.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    memories_data = [m.model_dump() for m in request.memories]
    created, failed = await crud_memory.bulk_set(
        db, project_id=request.project_id, memories=memories_data
    )
    
    return MemoryBulkResponse(created=created, failed=failed)


@router.post("/cleanup")
async def cleanup_expired_memories(
    project_id: UUID = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete expired memories (optionally for a specific project)"""
    if project_id and not await verify_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    count = await crud_memory.delete_expired(db, project_id=project_id)
    return {"message": f"Deleted {count} expired memories"}
