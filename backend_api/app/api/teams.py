"""
Teams API routes
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import team as crud_team
from app.crud import team_member as crud_team_member
from app.crud import user as crud_user
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithMembers,
    TeamMemberResponse,
    TeamMemberInvite,
    TeamMemberUpdate,
    TeamListResponse,
)
from app.api.deps import get_current_user, require_team_member, require_team_admin
from app.models.user import User
from app.models.team_member import TeamRole

router = APIRouter()


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all teams the user is a member of"""
    teams = await crud_team.get_user_teams(db, user_id=current_user.id)
    return TeamListResponse(teams=teams, total=len(teams))


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new team"""
    team = await crud_team.create_with_owner(
        db, obj_in=team_in, owner_id=current_user.id
    )
    return team


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_team_member),
):
    """Get team details"""
    team = await crud_team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    members_count = await crud_team.count_members(db, team_id=team_id)
    
    return TeamWithMembers(
        id=team.id,
        name=team.name,
        description=team.description,
        avatar_url=team.avatar_url,
        owner_id=team.owner_id,
        created_at=team.created_at,
        members_count=members_count,
    )


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_in: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_team_admin),
):
    """Update team details (admin only)"""
    team = await crud_team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    team = await crud_team.update(db, db_obj=team, obj_in=team_in)
    return team


@router.delete("/{team_id}")
async def delete_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete team (owner only)"""
    team = await crud_team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team owner can delete the team",
        )
    
    await crud_team.delete(db, id=team_id)
    return {"message": "Team deleted successfully"}


# Team Members
@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
async def list_team_members(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_team_member),
):
    """List all team members"""
    members = await crud_team_member.get_team_members(db, team_id=team_id)
    return members


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_team_member(
    team_id: UUID,
    invite: TeamMemberInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_team_admin),
):
    """Invite a user to the team by email (admin only)"""
    # Find user by email
    user = await crud_user.get_by_email(db, email=invite.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if already a member
    existing = await crud_team_member.get_by_team_and_user(
        db, team_id=team_id, user_id=user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team",
        )
    
    member = await crud_team_member.add_member(
        db,
        team_id=team_id,
        user_id=user.id,
        role=invite.role,
        invited_by=current_user.id,
    )
    return member


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: UUID,
    user_id: UUID,
    member_in: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_team_admin),
):
    """Update team member role (admin only)"""
    member = await crud_team_member.get_by_team_and_user(
        db, team_id=team_id, user_id=user_id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )
    
    # Cannot demote the team owner
    team = await crud_team.get(db, id=team_id)
    if team and team.owner_id == user_id and member_in.role != TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the team owner's role",
        )
    
    member = await crud_team_member.update_role(db, member=member, role=member_in.role)
    return member


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a team member (admin or self)"""
    # Check if user is admin or removing themselves
    is_admin = await crud_team_member.is_admin(db, team_id=team_id, user_id=current_user.id)
    is_self = user_id == current_user.id
    
    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required to remove other members",
        )
    
    # Cannot remove the team owner
    team = await crud_team.get(db, id=team_id)
    if team and team.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the team owner",
        )
    
    success = await crud_team_member.remove_member(db, team_id=team_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )
    
    return {"message": "Member removed successfully"}
