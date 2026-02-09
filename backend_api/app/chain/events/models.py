"""
Chain event models for audit logging
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Uuid, Text, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChainEvent(Base):
    """Chain event for audit logging with hash chaining"""
    
    __tablename__ = "chain_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    
    # Event details
    actor: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, system, ai_agent
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # AI Trust
    ai_risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low, medium, high
    
    # Chain hashing
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Additional data
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
        nullable=False,
    )
    
    __table_args__ = (
        Index("ix_chain_events_actor_timestamp", "actor", "timestamp"),
        Index("ix_chain_events_action_timestamp", "action", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<ChainEvent {self.event_id} - {self.action}>"
