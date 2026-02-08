"""
Memory model
"""
import uuid
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Memory(Base):
    """Memory model for AI context and project understanding"""
    
    __tablename__ = "memories"
    
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
    key: Mapped[str] = mapped_column(String(255), index=True)
    value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # For vector search (future enhancement)
    embedding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="memories")
    
    def __repr__(self) -> str:
        return f"<Memory {self.key}>"
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
