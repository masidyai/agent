"""
Billing schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.billing import BillingPlan, BillingStatus, UsageType, InvoiceStatus


class BillingBase(BaseModel):
    """Base billing schema"""
    plan: BillingPlan = BillingPlan.FREE


class BillingCreate(BillingBase):
    """Schema for creating billing record"""
    user_id: UUID


class BillingUpdate(BaseModel):
    """Schema for updating billing"""
    plan: Optional[BillingPlan] = None
    status: Optional[BillingStatus] = None


class BillingResponse(BillingBase):
    """Schema for billing response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    status: BillingStatus
    stripe_customer_id: Optional[str] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    usage_projects: int
    usage_executions: int
    usage_deployments: int
    usage_api_calls: int
    usage_github_repos: int
    cost_openai: float
    cost_docker: float
    cost_total: float
    limit_projects: int
    limit_executions: int
    limit_deployments: int
    limit_api_calls: int
    limit_repos: int
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    auto_renew: bool
    created_at: datetime


class UsageResponse(BaseModel):
    """Schema for usage statistics"""
    projects: int
    executions: int
    deployments: int
    api_calls: int
    github_repos: int
    cost_openai: float
    cost_docker: float
    cost_total: float
    limits: dict


class StripeCheckoutRequest(BaseModel):
    """Schema for creating Stripe checkout session"""
    plan: BillingPlan
    success_url: str
    cancel_url: str


class StripeCheckoutResponse(BaseModel):
    """Schema for Stripe checkout response"""
    checkout_url: str
    session_id: str


class StripeWebhookPayload(BaseModel):
    """Schema for Stripe webhook payload"""
    type: str
    data: dict


class PlanLimits(BaseModel):
    """Schema for plan limits"""
    projects: int
    executions: int
    deployments: int
    team_members: int
    api_calls: int
    github_repos: int
    price_monthly: float
    price_yearly: float
    features: list[str]


class PlansResponse(BaseModel):
    """Schema for available plans"""
    plans: dict[str, PlanLimits]


class UsageLogCreate(BaseModel):
    """Schema for creating usage log"""
    user_id: UUID
    usage_type: UsageType
    quantity: int
    cost: float
    metadata: Optional[dict] = None


class UsageLogResponse(BaseModel):
    """Schema for usage log response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    usage_type: UsageType
    quantity: int
    cost: float
    metadata: Optional[dict] = None
    timestamp: datetime


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    stripe_invoice_id: Optional[str] = None
    amount: float
    status: InvoiceStatus
    period_start: datetime
    period_end: datetime
    items: Optional[dict] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime


class InvoiceListResponse(BaseModel):
    """Schema for invoice list response"""
    invoices: list[InvoiceResponse]
    total: int
