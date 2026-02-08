"""
Deployment model
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class DeploymentEnvironment(str, Enum):
    """Deployment environment types"""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class DeploymentStatus(str, Enum):
    """Deployment status states"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    STOPPED = "stopped"


class DeploymentProvider(str, Enum):
    """Deployment provider types"""
    VERCEL = "vercel"
    RAILWAY = "railway"
    RENDER = "render"
    FLY = "fly"
    CUSTOM = "custom"


class Deployment(Base):
    """Deployment model for project deployments"""
    
    __tablename__ = "deployments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    environment: Mapped[DeploymentEnvironment] = mapped_column(
        SQLEnum(DeploymentEnvironment),
        default=DeploymentEnvironment.DEV,
    )
    status: Mapped[DeploymentStatus] = mapped_column(
        SQLEnum(DeploymentStatus),
        default=DeploymentStatus.PENDING,
    )
    provider: Mapped[DeploymentProvider] = mapped_column(
        SQLEnum(DeploymentProvider),
        default=DeploymentProvider.VERCEL,
    )
    
    # Deployment details
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    build_logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deploy_logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Provider-specific IDs
    provider_deployment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Metadata
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    branch: Mapped[str] = mapped_column(String(255), default="main")
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="deployments")
    
    def __repr__(self) -> str:
        return f"<Deployment {self.id} - {self.status}>"
