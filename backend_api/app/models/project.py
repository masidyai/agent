"""
Project model
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid, Enum as SQLEnum, Boolean, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team
    from app.models.deployment import Deployment
    from app.models.memory import Memory
    from app.models.execution import Execution
    from app.models.project_file import ProjectFile


class ProjectStatus(str, Enum):
    """Project status states"""
    DRAFT = "draft"
    PENDING = "pending"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProjectFlow(str, Enum):
    """Project flow types"""
    SAAS = "saas"
    API = "api"
    REFACTOR = "refactor"


class Project(Base):
    """Project model for AI-generated applications"""
    
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flow: Mapped[ProjectFlow] = mapped_column(
        SQLEnum(ProjectFlow),
        default=ProjectFlow.SAAS,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT,
    )
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    files_count: Mapped[str] = mapped_column(String(10), default="0")
    steps_completed: Mapped[str] = mapped_column(String(10), default="0")
    steps_total: Mapped[str] = mapped_column(String(10), default="0")
    
    # GitHub integration fields
    github_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_repo_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_repo_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    github_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    github_last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    github_topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of topics
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="projects")
    deployments: Mapped[List["Deployment"]] = relationship(
        "Deployment",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    memories: Mapped[List["Memory"]] = relationship(
        "Memory",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    executions: Mapped[List["Execution"]] = relationship(
        "Execution",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    files: Mapped[List["ProjectFile"]] = relationship(
        "ProjectFile",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.name}>"
