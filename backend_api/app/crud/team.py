"""
Team and TeamMember CRUD operations
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberCreate, TeamMemberUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    """CRUD operations for Team model"""
    
    async def create_with_owner(
        self,
        db: AsyncSession,
        *,
        obj_in: TeamCreate,
        owner_id: UUID,
    ) -> Team:
        """Create a new team with owner as admin member"""
        db_obj = Team(
            name=obj_in.name,
            description=obj_in.description,
            avatar_url=obj_in.avatar_url,
            owner_id=owner_id,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        
        # Add owner as admin member
        member = TeamMember(
            team_id=db_obj.id,
            user_id=owner_id,
            role=TeamRole.ADMIN,
            joined_at=datetime.utcnow(),
        )
        db.add(member)
        await db.flush()
        
        return db_obj
    
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Team]:
        """Get teams owned by a user"""
        result = await db.execute(
            select(Team)
            .where(Team.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_user_teams(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Team]:
        """Get all teams a user is a member of"""
        result = await db.execute(
            select(Team)
            .join(TeamMember, Team.id == TeamMember.team_id)
            .where(TeamMember.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_members(self, db: AsyncSession, *, team_id: UUID) -> int:
        """Count team members"""
        result = await db.execute(
            select(func.count())
            .select_from(TeamMember)
            .where(TeamMember.team_id == team_id)
        )
        return result.scalar() or 0


class CRUDTeamMember(CRUDBase[TeamMember, TeamMemberCreate, TeamMemberUpdate]):
    """CRUD operations for TeamMember model"""
    
    async def get_by_team_and_user(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        user_id: UUID,
    ) -> Optional[TeamMember]:
        """Get team member by team and user"""
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def get_team_members(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TeamMember]:
        """Get all members of a team"""
        result = await db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def add_member(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        user_id: UUID,
        role: TeamRole = TeamRole.MEMBER,
        invited_by: Optional[UUID] = None,
    ) -> TeamMember:
        """Add a new member to a team"""
        db_obj = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
            joined_at=datetime.utcnow(),
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_role(
        self,
        db: AsyncSession,
        *,
        member: TeamMember,
        role: TeamRole,
    ) -> TeamMember:
        """Update member role"""
        member.role = role
        db.add(member)
        await db.flush()
        await db.refresh(member)
        return member
    
    async def remove_member(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Remove a member from a team"""
        member = await self.get_by_team_and_user(db, team_id=team_id, user_id=user_id)
        if member:
            await db.delete(member)
            await db.flush()
            return True
        return False
    
    async def is_admin(
        self,
        db: AsyncSession,
        *,
        team_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Check if user is admin of team"""
        member = await self.get_by_team_and_user(db, team_id=team_id, user_id=user_id)
        return member is not None and member.role == TeamRole.ADMIN


team = CRUDTeam(Team)
team_member = CRUDTeamMember(TeamMember)
