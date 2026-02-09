"""
User CRUD operations
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.billing import Billing, BillingPlan
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model"""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_oauth(
        self,
        db: AsyncSession,
        *,
        provider: str,
        oauth_id: str,
    ) -> Optional[User]:
        """Get user by OAuth provider and ID"""
        result = await db.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_id == oauth_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password"""
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            name=obj_in.name,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        
        # Create default billing record
        billing = Billing(
            user_id=db_obj.id,
            plan=BillingPlan.FREE,
        )
        db.add(billing)
        await db.flush()
        
        return db_obj
    
    async def create_oauth_user(
        self,
        db: AsyncSession,
        *,
        email: str,
        name: Optional[str],
        avatar_url: Optional[str],
        provider: str,
        oauth_id: str,
    ) -> User:
        """Create a new OAuth user"""
        db_obj = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
            is_verified=True,  # OAuth users are auto-verified
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        
        # Create default billing record
        billing = Billing(
            user_id=db_obj.id,
            plan=BillingPlan.FREE,
        )
        db.add(billing)
        await db.flush()
        
        return db_obj
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.password_hash:
            return None  # OAuth user without password
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    async def update_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        new_password: str,
    ) -> User:
        """Update user password"""
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    
    async def verify_user(self, db: AsyncSession, *, user: User) -> User:
        """Mark user as verified"""
        user.is_verified = True
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    
    async def deactivate(self, db: AsyncSession, *, user: User) -> User:
        """Deactivate user account"""
        user.is_active = False
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user


user = CRUDUser(User)
