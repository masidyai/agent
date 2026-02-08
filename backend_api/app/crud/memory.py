"""
Memory CRUD operations
"""
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryUpdate


class CRUDMemory(CRUDBase[Memory, MemoryCreate, MemoryUpdate]):
    """CRUD operations for Memory model"""
    
    async def get_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
    ) -> list[Memory]:
        """Get all memories for a project"""
        query = select(Memory).where(Memory.project_id == project_id)
        
        if category:
            query = query.where(Memory.category == category)
        
        query = query.order_by(Memory.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_key(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        key: str,
    ) -> Optional[Memory]:
        """Get a memory by project and key"""
        result = await db.execute(
            select(Memory).where(
                Memory.project_id == project_id,
                Memory.key == key,
            )
        )
        return result.scalar_one_or_none()
    
    async def set_memory(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        key: str,
        value: Any,
        category: Optional[str] = None,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Memory:
        """Set or update a memory entry"""
        existing = await self.get_by_key(db, project_id=project_id, key=key)
        
        if existing:
            existing.value = value
            if category is not None:
                existing.category = category
            if description is not None:
                existing.description = description
            if expires_at is not None:
                existing.expires_at = expires_at
            db.add(existing)
            await db.flush()
            await db.refresh(existing)
            return existing
        
        db_obj = Memory(
            project_id=project_id,
            key=key,
            value=value,
            category=category,
            description=description,
            expires_at=expires_at,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_value(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get memory value by key, return default if not found"""
        memory = await self.get_by_key(db, project_id=project_id, key=key)
        if memory is None or memory.is_expired:
            return default
        return memory.value
    
    async def search_memories(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> list[Memory]:
        """Search memories by key or description"""
        search_pattern = f"%{query}%"
        conditions = [
            Memory.project_id == project_id,
            or_(
                Memory.key.ilike(search_pattern),
                Memory.description.ilike(search_pattern),
            )
        ]
        
        if category:
            conditions.append(Memory.category == category)
        
        result = await db.execute(
            select(Memory)
            .where(and_(*conditions))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def delete_by_key(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        key: str,
    ) -> bool:
        """Delete a memory by key"""
        memory = await self.get_by_key(db, project_id=project_id, key=key)
        if memory:
            await db.delete(memory)
            await db.flush()
            return True
        return False
    
    async def delete_by_category(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        category: str,
    ) -> int:
        """Delete all memories in a category"""
        result = await db.execute(
            delete(Memory)
            .where(
                Memory.project_id == project_id,
                Memory.category == category,
            )
            .returning(Memory.id)
        )
        deleted_ids = result.all()
        await db.flush()
        return len(deleted_ids)
    
    async def delete_expired(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[UUID] = None,
    ) -> int:
        """Delete expired memories"""
        query = delete(Memory).where(
            Memory.expires_at.isnot(None),
            Memory.expires_at < datetime.utcnow(),
        )
        
        if project_id:
            query = query.where(Memory.project_id == project_id)
        
        result = await db.execute(query.returning(Memory.id))
        deleted_ids = result.all()
        await db.flush()
        return len(deleted_ids)
    
    async def bulk_set(
        self,
        db: AsyncSession,
        *,
        project_id: UUID,
        memories: list[dict],
    ) -> tuple[int, int]:
        """Bulk set memories. Returns (created_count, failed_count)"""
        created = 0
        failed = 0
        
        for mem in memories:
            try:
                await self.set_memory(
                    db,
                    project_id=project_id,
                    key=mem.get("key"),
                    value=mem.get("value"),
                    category=mem.get("category"),
                    description=mem.get("description"),
                )
                created += 1
            except Exception:
                failed += 1
        
        return created, failed


memory = CRUDMemory(Memory)
