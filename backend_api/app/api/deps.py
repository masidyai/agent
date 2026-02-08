"""
API dependencies for authentication and authorization
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.crud import user as crud_user
from app.crud import team_member as crud_team_member
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """Get current authenticated user from JWT token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = verify_token(token, token_type="access")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await crud_user.get(db, id=UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not token:
        return None
    
    user_id = verify_token(token, token_type="access")
    if not user_id:
        return None
    
    user = await crud_user.get(db, id=UUID(user_id))
    if not user or not user.is_active:
        return None
    
    return user


async def get_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require a verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user


class TeamPermission:
    """Dependency for checking team permissions"""
    
    def __init__(self, require_admin: bool = False):
        self.require_admin = require_admin
    
    async def __call__(
        self,
        team_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Check if user has permission for the team"""
        member = await crud_team_member.get_by_team_and_user(
            db, team_id=team_id, user_id=current_user.id
        )
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this team",
            )
        
        if self.require_admin:
            from app.models.team_member import TeamRole
            if member.role != TeamRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin permission required",
                )
        
        return current_user


# Pre-configured permission checkers
require_team_member = TeamPermission(require_admin=False)
require_team_admin = TeamPermission(require_admin=True)
