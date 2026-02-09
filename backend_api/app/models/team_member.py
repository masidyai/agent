"""
TeamMember model
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team


class TeamRole(str, Enum):
    """Team member roles"""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamMember(Base):
    """TeamMember model for team membership and roles"""
    
    __tablename__ = "team_members"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("teams.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[TeamRole] = mapped_column(
        SQLEnum(TeamRole),
        default=TeamRole.MEMBER,
    )
    invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    invited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships")
    
    def __repr__(self) -> str:
        return f"<TeamMember {self.user_id} in {self.team_id}>"
