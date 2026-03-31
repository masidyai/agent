"""
Identity and key vault models
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Uuid, Enum as SQLEnum, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class KeyStatus(str, Enum):
    """Status of encryption keys"""
    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"


class MasidyIdentity(Base):
    """Masidy Identity - unique identity for each user"""
    
    __tablename__ = "masidy_identities"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    masidy_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    root_key_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    root_keys: Mapped[list["RootKey"]] = relationship(
        "RootKey",
        back_populates="identity",
        cascade="all, delete-orphan",
    )
    derived_keys: Mapped[list["DerivedKey"]] = relationship(
        "DerivedKey",
        back_populates="identity",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<MasidyIdentity {self.masidy_id}>"


class RootKey(Base):
    """Root encryption key for Masidy Identity"""
    
    __tablename__ = "root_keys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    key_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    masidy_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("masidy_identities.masidy_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[KeyStatus] = mapped_column(
        SQLEnum(KeyStatus),
        default=KeyStatus.ACTIVE,
        index=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    identity: Mapped["MasidyIdentity"] = relationship("MasidyIdentity", back_populates="root_keys")
    
    __table_args__ = (
        Index("ix_root_keys_masidy_status", "masidy_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<RootKey {self.key_id} - {self.status}>"


class DerivedKey(Base):
    """Derived key for specific scopes (projects, integrations, etc.)"""
    
    __tablename__ = "derived_keys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    key_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    masidy_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("masidy_identities.masidy_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    scope: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scope_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    identity: Mapped["MasidyIdentity"] = relationship("MasidyIdentity", back_populates="derived_keys")
    
    __table_args__ = (
        Index("ix_derived_keys_masidy_scope", "masidy_id", "scope"),
    )
    
    def __repr__(self) -> str:
        return f"<DerivedKey {self.key_id} - {self.scope}>"
