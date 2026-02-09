"""
Execution model for tracking code execution sessions
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid, Enum as SQLEnum, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ExecutionStatus(str, Enum):
    """Execution status states"""
    PENDING = "pending"
    BUILDING = "building"
    LINTING = "linting"
    TESTING = "testing"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ExecutionPhase(str, Enum):
    """Execution pipeline phases"""
    VALIDATION = "validation"
    BUILD = "build"
    LINT = "lint"
    TEST = "test"
    EXECUTION = "execution"
    CLEANUP = "cleanup"


class Execution(Base):
    """Execution model for tracking code execution sessions"""
    
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
    
    # Basic info
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    command: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus),
        default=ExecutionStatus.PENDING,
    )
    current_phase: Mapped[Optional[ExecutionPhase]] = mapped_column(
        SQLEnum(ExecutionPhase),
        nullable=True,
    )
    
    # Build phase
    build_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    build_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Lint phase
    lint_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lint_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lint_issues: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Test phase
    test_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    test_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tests_passed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tests_failed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    test_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Execution phase
    execution_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exit_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Validation & errors
    validation_errors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    runtime_errors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Performance metrics
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_used_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Docker container info
    container_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    container_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="executions")
    
    def __repr__(self) -> str:
        return f"<Execution {self.id} - {self.status}>"
    
    @property
    def is_running(self) -> bool:
        """Check if execution is currently running"""
        return self.status in [
            ExecutionStatus.BUILDING,
            ExecutionStatus.LINTING,
            ExecutionStatus.TESTING,
            ExecutionStatus.RUNNING,
        ]
    
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed (success or failure)"""
        return self.status in [
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.CANCELLED,
        ]
