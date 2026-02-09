"""
Billing model
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Integer, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BillingPlan(str, Enum):
    """Billing plan types"""
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class BillingStatus(str, Enum):
    """Billing status states"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"


class Billing(Base):
    """Billing model for subscriptions and usage tracking"""
    
    __tablename__ = "billing"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    plan: Mapped[BillingPlan] = mapped_column(
        SQLEnum(BillingPlan),
        default=BillingPlan.FREE,
    )
    status: Mapped[BillingStatus] = mapped_column(
        SQLEnum(BillingStatus),
        default=BillingStatus.ACTIVE,
    )
    
    # Stripe integration
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Usage tracking
    usage_projects: Mapped[int] = mapped_column(Integer, default=0)
    usage_executions: Mapped[int] = mapped_column(Integer, default=0)
    usage_deployments: Mapped[int] = mapped_column(Integer, default=0)
    usage_api_calls: Mapped[int] = mapped_column(Integer, default=0)
    
    # Limits based on plan
    limit_projects: Mapped[int] = mapped_column(Integer, default=3)
    limit_executions: Mapped[int] = mapped_column(Integer, default=10)
    limit_deployments: Mapped[int] = mapped_column(Integer, default=1)
    
    # Billing cycle
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="billing")
    
    def __repr__(self) -> str:
        return f"<Billing {self.user_id} - {self.plan}>"
    
    @property
    def is_over_project_limit(self) -> bool:
        return self.usage_projects >= self.limit_projects
    
    @property
    def is_over_execution_limit(self) -> bool:
        return self.limit_executions != -1 and self.usage_executions >= self.limit_executions
    
    @property
    def is_over_api_call_limit(self) -> bool:
        return self.limit_api_calls != -1 and self.usage_api_calls >= self.limit_api_calls
    
    @property
    def is_trial_active(self) -> bool:
        """Check if trial period is still active"""
        if not self.trial_end:
            return False
        return datetime.utcnow() < self.trial_end
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired"""
        if not self.trial_end:
            return False
        return datetime.utcnow() >= self.trial_end


class UsageLog(Base):
    """Detailed usage tracking log"""
    
    __tablename__ = "usage_logs"
    
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
    usage_type: Mapped[UsageType] = mapped_column(SQLEnum(UsageType), index=True)
    
    # Quantity and cost
    quantity: Mapped[int] = mapped_column(Integer, default=1)  # tokens, minutes, count
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Extra data (flexible JSON for usage-specific data)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<UsageLog {self.user_id} - {self.usage_type} - ${self.cost}>"


class Invoice(Base):
    """Invoice/billing history"""
    
    __tablename__ = "invoices"
    
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
    
    # Stripe integration
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    
    # Invoice details
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Billing period
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    
    # Usage breakdown (JSON field for flexible itemization)
    items: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Invoice {self.user_id} - ${self.amount} - {self.status}>"
