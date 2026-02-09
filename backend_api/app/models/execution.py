"""
Execution and ExecutionStep models
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ExecutionStatus(str, Enum):
    """Execution status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class StepStatus(str, Enum):
    """Step status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Execution(Base):
    """Execution model for tracking project builds"""
    
    __tablename__ = "executions"
    
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
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus),
        default=ExecutionStatus.PENDING,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="executions")
    steps: Mapped[List["ExecutionStep"]] = relationship(
        "ExecutionStep",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="ExecutionStep.step_number",
    )
    
    def __repr__(self) -> str:
        return f"<Execution {self.id} - {self.status}>"


class ExecutionStep(Base):
    """ExecutionStep model for tracking individual build steps"""
    
    __tablename__ = "execution_steps"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("executions.id", ondelete="CASCADE"),
        index=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tool_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[StepStatus] = mapped_column(
        SQLEnum(StepStatus),
        default=StepStatus.PENDING,
    )
    output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    execution: Mapped["Execution"] = relationship("Execution", back_populates="steps")
    
    def __repr__(self) -> str:
        return f"<ExecutionStep {self.step_number}: {self.name} - {self.status}>"
