"""
Billing CRUD operations
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.billing import Billing, BillingPlan, BillingStatus
from app.schemas.billing import BillingCreate, BillingUpdate


# Plan limits configuration
PLAN_LIMITS = {
    BillingPlan.FREE: {
        "projects": 3,
        "executions": 10,
        "deployments": 1,
        "team_members": 0,
    },
    BillingPlan.PRO: {
        "projects": 25,
        "executions": 100,
        "deployments": 5,
        "team_members": 0,
    },
    BillingPlan.TEAM: {
        "projects": 100,
        "executions": 500,
        "deployments": 20,
        "team_members": 10,
    },
    BillingPlan.ENTERPRISE: {
        "projects": -1,  # Unlimited
        "executions": -1,
        "deployments": -1,
        "team_members": -1,
    },
}


class CRUDBilling(CRUDBase[Billing, BillingCreate, BillingUpdate]):
    """CRUD operations for Billing model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
    ) -> Optional[Billing]:
        """Get billing record by user ID"""
        result = await db.execute(
            select(Billing).where(Billing.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_stripe_customer(
        self,
        db: AsyncSession,
        *,
        stripe_customer_id: str,
    ) -> Optional[Billing]:
        """Get billing by Stripe customer ID"""
        result = await db.execute(
            select(Billing).where(Billing.stripe_customer_id == stripe_customer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_stripe_subscription(
        self,
        db: AsyncSession,
        *,
        stripe_subscription_id: str,
    ) -> Optional[Billing]:
        """Get billing by Stripe subscription ID"""
        result = await db.execute(
            select(Billing).where(Billing.stripe_subscription_id == stripe_subscription_id)
        )
        return result.scalar_one_or_none()
    
    async def create_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
    ) -> Billing:
        """Create default billing record for a user"""
        limits = PLAN_LIMITS[BillingPlan.FREE]
        db_obj = Billing(
            user_id=user_id,
            plan=BillingPlan.FREE,
            status=BillingStatus.ACTIVE,
            limit_projects=limits["projects"],
            limit_executions=limits["executions"],
            limit_deployments=limits["deployments"],
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_plan(
        self,
        db: AsyncSession,
        *,
        billing: Billing,
        plan: BillingPlan,
    ) -> Billing:
        """Update billing plan and limits"""
        limits = PLAN_LIMITS[plan]
        billing.plan = plan
        billing.limit_projects = limits["projects"]
        billing.limit_executions = limits["executions"]
        billing.limit_deployments = limits["deployments"]
        db.add(billing)
        await db.flush()
        await db.refresh(billing)
        return billing
    
    async def update_stripe_info(
        self,
        db: AsyncSession,
        *,
        billing: Billing,
        stripe_customer_id: str,
        stripe_subscription_id: Optional[str] = None,
        stripe_price_id: Optional[str] = None,
    ) -> Billing:
        """Update Stripe integration info"""
        billing.stripe_customer_id = stripe_customer_id
        if stripe_subscription_id:
            billing.stripe_subscription_id = stripe_subscription_id
        if stripe_price_id:
            billing.stripe_price_id = stripe_price_id
        db.add(billing)
        await db.flush()
        await db.refresh(billing)
        return billing
    
    async def increment_usage(
        self,
        db: AsyncSession,
        *,
        billing: Billing,
        projects: int = 0,
        executions: int = 0,
        deployments: int = 0,
        api_calls: int = 0,
    ) -> Billing:
        """Increment usage counters"""
        billing.usage_projects += projects
        billing.usage_executions += executions
        billing.usage_deployments += deployments
        billing.usage_api_calls += api_calls
        db.add(billing)
        await db.flush()
        await db.refresh(billing)
        return billing
    
    async def reset_usage(
        self,
        db: AsyncSession,
        *,
        billing: Billing,
    ) -> Billing:
        """Reset usage counters (for new billing period)"""
        billing.usage_projects = 0
        billing.usage_executions = 0
        billing.usage_deployments = 0
        billing.usage_api_calls = 0
        db.add(billing)
        await db.flush()
        await db.refresh(billing)
        return billing
    
    async def check_limit(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        limit_type: str,  # projects, executions, deployments
    ) -> tuple[bool, int, int]:
        """Check if user is within usage limits. Returns (is_ok, current, limit)"""
        billing = await self.get_by_user(db, user_id=user_id)
        if not billing:
            return False, 0, 0
        
        usage_map = {
            "projects": (billing.usage_projects, billing.limit_projects),
            "executions": (billing.usage_executions, billing.limit_executions),
            "deployments": (billing.usage_deployments, billing.limit_deployments),
        }
        
        current, limit = usage_map.get(limit_type, (0, 0))
        
        # -1 means unlimited
        if limit == -1:
            return True, current, limit
        
        return current < limit, current, limit


class CRUDUsageLog(CRUDBase[UsageLog, UsageLogCreate, None]):
    """CRUD operations for UsageLog model"""
    
    async def create_log(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        usage_type: UsageType,
        quantity: int,
        cost: float,
        extra_data: Optional[dict] = None,
    ) -> UsageLog:
        """Create a usage log entry"""
        db_obj = UsageLog(
            user_id=user_id,
            usage_type=usage_type,
            quantity=quantity,
            cost=cost,
            extra_data=extra_data,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_logs(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        usage_type: Optional[UsageType] = None,
        limit: int = 100,
    ) -> list[UsageLog]:
        """Get usage logs for a user with optional filters"""
        query = select(UsageLog).where(UsageLog.user_id == user_id)
        
        if start_date:
            query = query.where(UsageLog.timestamp >= start_date)
        if end_date:
            query = query.where(UsageLog.timestamp <= end_date)
        if usage_type:
            query = query.where(UsageLog.usage_type == usage_type)
        
        query = query.order_by(UsageLog.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())


class CRUDInvoice(CRUDBase[Invoice, None, None]):
    """CRUD operations for Invoice model"""
    
    async def create_invoice(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        amount: float,
        period_start: datetime,
        period_end: datetime,
        items: Optional[dict] = None,
        stripe_invoice_id: Optional[str] = None,
    ) -> Invoice:
        """Create an invoice"""
        db_obj = Invoice(
            user_id=user_id,
            amount=amount,
            status=InvoiceStatus.DRAFT,
            period_start=period_start,
            period_end=period_end,
            items=items,
            stripe_invoice_id=stripe_invoice_id,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_invoices(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        limit: int = 50,
    ) -> list[Invoice]:
        """Get invoices for a user"""
        result = await db.execute(
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_stripe_invoice(
        self,
        db: AsyncSession,
        *,
        stripe_invoice_id: str,
    ) -> Optional[Invoice]:
        """Get invoice by Stripe invoice ID"""
        result = await db.execute(
            select(Invoice).where(Invoice.stripe_invoice_id == stripe_invoice_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        invoice: Invoice,
        status: InvoiceStatus,
        paid_at: Optional[datetime] = None,
    ) -> Invoice:
        """Update invoice status"""
        invoice.status = status
        if paid_at:
            invoice.paid_at = paid_at
        db.add(invoice)
        await db.flush()
        await db.refresh(invoice)
        return invoice


billing = CRUDBilling(Billing)
