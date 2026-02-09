"""
Billing API routes
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.crud import billing as crud_billing
from app.crud.billing import PLAN_LIMITS, usage_log as crud_usage_log, invoice as crud_invoice
from app.schemas.billing import (
    BillingResponse,
    UsageResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    PlanLimits,
    PlansResponse,
    UsageLogResponse,
    InvoiceListResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.billing import BillingPlan, BillingStatus, InvoiceStatus

router = APIRouter()


@router.get("/", response_model=BillingResponse)
async def get_billing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's billing information"""
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.billing.create_for_user(db, user_id=current_user.id)
    return billing


@router.get("/tier", response_model=BillingResponse)
async def get_tier(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current tier information"""
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.billing.create_for_user(db, user_id=current_user.id)
    return billing


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current usage statistics"""
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.billing.create_for_user(db, user_id=current_user.id)
    
    return UsageResponse(
        projects=billing.usage_projects,
        executions=billing.usage_executions,
        deployments=billing.usage_deployments,
        api_calls=billing.usage_api_calls,
        github_repos=billing.usage_github_repos,
        cost_openai=billing.cost_openai,
        cost_docker=billing.cost_docker,
        cost_total=billing.cost_total,
        limits={
            "projects": billing.limit_projects,
            "executions": billing.limit_executions,
            "deployments": billing.limit_deployments,
            "api_calls": billing.limit_api_calls,
            "github_repos": billing.limit_repos,
        },
    )


@router.get("/usage/logs", response_model=list[UsageLogResponse])
async def get_usage_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed usage logs"""
    logs = await crud_usage_log.get_user_logs(
        db,
        user_id=current_user.id,
        limit=limit,
    )
    return logs


@router.get("/invoices", response_model=InvoiceListResponse)
async def get_invoices(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get past invoices"""
    invoices = await crud_invoice.get_user_invoices(
        db,
        user_id=current_user.id,
        limit=limit,
    )
    return InvoiceListResponse(invoices=invoices, total=len(invoices))


@router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """Get available billing plans"""
    plans = {
        "free": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.FREE]["projects"],
            executions=PLAN_LIMITS[BillingPlan.FREE]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.FREE]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.FREE]["team_members"],
            api_calls=PLAN_LIMITS[BillingPlan.FREE]["api_calls"],
            github_repos=PLAN_LIMITS[BillingPlan.FREE]["github_repos"],
            price_monthly=0,
            price_yearly=0,
            features=[
                "5 projects",
                "10 OpenAI API calls",
                "5 Docker executions",
                "1 GitHub repo",
                "7-day free trial",
            ],
        ),
        "pro": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.PRO]["projects"],
            executions=PLAN_LIMITS[BillingPlan.PRO]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.PRO]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.PRO]["team_members"],
            api_calls=PLAN_LIMITS[BillingPlan.PRO]["api_calls"],
            github_repos=PLAN_LIMITS[BillingPlan.PRO]["github_repos"],
            price_monthly=29,
            price_yearly=290,
            features=[
                "50 projects",
                "100 OpenAI API calls",
                "50 Docker executions",
                "50 GitHub repos",
                "Advanced analytics",
                "Priority support",
            ],
        ),
        "team": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.TEAM]["projects"],
            executions=PLAN_LIMITS[BillingPlan.TEAM]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.TEAM]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.TEAM]["team_members"],
            api_calls=PLAN_LIMITS[BillingPlan.TEAM]["api_calls"],
            github_repos=PLAN_LIMITS[BillingPlan.TEAM]["github_repos"],
            price_monthly=99,
            price_yearly=990,
            features=[
                "100 projects",
                "500 OpenAI API calls",
                "500 executions",
                "100 GitHub repos",
                "Team collaboration (10 members)",
                "Admin controls",
                "Priority support",
            ],
        ),
        "enterprise": PlanLimits(
            projects=-1,
            executions=-1,
            deployments=-1,
            team_members=-1,
            api_calls=-1,
            github_repos=-1,
            price_monthly=0,  # Custom pricing
            price_yearly=0,
            features=[
                "Unlimited projects",
                "Unlimited API calls",
                "Unlimited executions",
                "Unlimited repos",
                "Unlimited team members",
                "SSO/SAML",
                "Dedicated support",
                "Custom workflows",
                "SLA guarantees",
            ],
        ),
    }
    return PlansResponse(plans=plans)


@router.post("/checkout", response_model=StripeCheckoutResponse)
async def create_checkout_session(
    request: StripeCheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe checkout session for plan upgrade"""
    if not settings.STRIPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )
    
    if request.plan == BillingPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout for free plan",
        )
    
    if request.plan == BillingPlan.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact sales for enterprise plan",
        )
    
    # Get or create billing record
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.billing.create_for_user(db, user_id=current_user.id)
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Create or get Stripe customer
        if not billing.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=getattr(current_user, 'name', current_user.email),
                metadata={"user_id": str(current_user.id)},
            )
            await crud_billing.billing.update_stripe_info(
                db, billing=billing, stripe_customer_id=customer.id
            )
            customer_id = customer.id
        else:
            customer_id = billing.stripe_customer_id
        
        # Get price ID based on plan
        price_id = (
            settings.STRIPE_PRICE_ID_PRO 
            if request.plan == BillingPlan.PRO 
            else settings.STRIPE_PRICE_ID_TEAM
        )
        
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe price not configured",
            )
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={"user_id": str(current_user.id), "plan": request.plan.value},
        )
        
        return StripeCheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe library not installed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.post("/upgrade")
async def upgrade_plan(
    plan: BillingPlan,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upgrade to a different plan (redirects to Stripe checkout)"""
    if plan == BillingPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upgrade to free plan. Use downgrade instead.",
        )
    
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing record not found",
        )
    
    if billing.plan == plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this plan",
        )
    
    return {
        "message": "Please use the checkout endpoint to upgrade",
        "plan": plan.value,
    }


@router.post("/downgrade")
async def downgrade_plan(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Downgrade plan to free tier"""
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing record not found",
        )
    
    if billing.plan == BillingPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on free plan",
        )
    
    # Cancel Stripe subscription if exists
    if billing.stripe_subscription_id and settings.STRIPE_API_KEY:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_API_KEY
            stripe.Subscription.modify(
                billing.stripe_subscription_id,
                cancel_at_period_end=True,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel subscription: {str(e)}",
            )
    
    # Update to free plan
    await crud_billing.billing.update_plan(db, billing=billing, plan=BillingPlan.FREE)
    
    return {"message": "Downgraded to free plan at end of billing period"}


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel current subscription"""
    if not settings.STRIPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )
    
    billing = await crud_billing.billing.get_by_user(db, user_id=current_user.id)
    if not billing or not billing.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription",
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Cancel at period end
        stripe.Subscription.modify(
            billing.stripe_subscription_id,
            cancel_at_period_end=True,
        )
        
        return {"message": "Subscription will be canceled at the end of the billing period"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}",
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
):
    """Handle Stripe webhooks (called by Stripe)"""
    if not settings.STRIPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Get the raw body
        payload = await request.body()
        
        # Verify webhook signature if webhook secret is configured
        if settings.STRIPE_WEBHOOK_SECRET and stripe_signature:
            try:
                event = stripe.Webhook.construct_event(
                    payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
                )
            except stripe.error.SignatureVerificationError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid signature",
                )
        else:
            # For testing without signature verification
            event = json.loads(payload)
        
        # Handle different event types
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        if event_type == "customer.subscription.created":
            await handle_subscription_created(db, data)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(db, data)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(db, data)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(db, data)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(db, data)
        elif event_type == "customer.updated":
            await handle_customer_updated(db, data)
        
        return {"received": True}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook error: {str(e)}",
        )


async def handle_subscription_created(db: AsyncSession, subscription: dict):
    """Handle subscription created event"""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status_str = subscription.get("status")
    
    billing = await crud_billing.billing.get_by_stripe_customer(
        db, stripe_customer_id=customer_id
    )
    
    if billing:
        # Update subscription info
        billing.stripe_subscription_id = subscription_id
        billing.status = BillingStatus.ACTIVE if status_str == "active" else BillingStatus.TRIALING
        
        # Extract period dates
        current_period_start = subscription.get("current_period_start")
        current_period_end = subscription.get("current_period_end")
        
        if current_period_start:
            billing.current_period_start = datetime.fromtimestamp(current_period_start)
        if current_period_end:
            billing.current_period_end = datetime.fromtimestamp(current_period_end)
        
        # Determine plan from price
        price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
        if price_id == settings.STRIPE_PRICE_ID_PRO:
            await crud_billing.billing.update_plan(db, billing=billing, plan=BillingPlan.PRO)
        elif price_id == settings.STRIPE_PRICE_ID_TEAM:
            await crud_billing.billing.update_plan(db, billing=billing, plan=BillingPlan.TEAM)
        
        await db.commit()


async def handle_subscription_updated(db: AsyncSession, subscription: dict):
    """Handle subscription updated event"""
    subscription_id = subscription.get("id")
    status_str = subscription.get("status")
    
    billing = await crud_billing.billing.get_by_stripe_subscription(
        db, stripe_subscription_id=subscription_id
    )
    
    if billing:
        # Update status
        if status_str == "active":
            billing.status = BillingStatus.ACTIVE
        elif status_str == "past_due":
            billing.status = BillingStatus.PAST_DUE
        elif status_str == "canceled":
            billing.status = BillingStatus.CANCELED
        
        # Update period dates
        current_period_start = subscription.get("current_period_start")
        current_period_end = subscription.get("current_period_end")
        
        if current_period_start:
            billing.current_period_start = datetime.fromtimestamp(current_period_start)
        if current_period_end:
            billing.current_period_end = datetime.fromtimestamp(current_period_end)
        
        # Reset usage if new period started
        if current_period_start:
            await crud_billing.billing.reset_usage(db, billing=billing)
        
        await db.commit()


async def handle_subscription_deleted(db: AsyncSession, subscription: dict):
    """Handle subscription deleted/canceled event"""
    subscription_id = subscription.get("id")
    
    billing = await crud_billing.billing.get_by_stripe_subscription(
        db, stripe_subscription_id=subscription_id
    )
    
    if billing:
        billing.status = BillingStatus.CANCELED
        # Downgrade to free plan
        await crud_billing.billing.update_plan(db, billing=billing, plan=BillingPlan.FREE)
        await db.commit()


async def handle_payment_succeeded(db: AsyncSession, invoice_data: dict):
    """Handle successful payment"""
    customer_id = invoice_data.get("customer")
    invoice_id = invoice_data.get("id")
    amount = invoice_data.get("amount_paid", 0) / 100  # Convert cents to dollars
    
    billing = await crud_billing.billing.get_by_stripe_customer(
        db, stripe_customer_id=customer_id
    )
    
    if billing:
        # Create or update invoice record
        existing_invoice = await crud_invoice.get_by_stripe_invoice(
            db, stripe_invoice_id=invoice_id
        )
        
        if not existing_invoice:
            period_start = invoice_data.get("period_start")
            period_end = invoice_data.get("period_end")
            
            await crud_invoice.create_invoice(
                db,
                user_id=billing.user_id,
                amount=amount,
                period_start=datetime.fromtimestamp(period_start) if period_start else datetime.utcnow(),
                period_end=datetime.fromtimestamp(period_end) if period_end else datetime.utcnow(),
                stripe_invoice_id=invoice_id,
            )
        
        # Update invoice status
        invoice_obj = await crud_invoice.get_by_stripe_invoice(db, stripe_invoice_id=invoice_id)
        if invoice_obj:
            await crud_invoice.update_status(
                db,
                invoice=invoice_obj,
                status=InvoiceStatus.PAID,
                paid_at=datetime.utcnow(),
            )
        
        # Ensure billing is active
        billing.status = BillingStatus.ACTIVE
        await db.commit()


async def handle_payment_failed(db: AsyncSession, invoice_data: dict):
    """Handle failed payment"""
    customer_id = invoice_data.get("customer")
    
    billing = await crud_billing.billing.get_by_stripe_customer(
        db, stripe_customer_id=customer_id
    )
    
    if billing:
        billing.status = BillingStatus.PAST_DUE
        await db.commit()


async def handle_customer_updated(db: AsyncSession, customer: dict):
    """Handle customer updated event"""
    customer_id = customer.get("id")
    
    billing = await crud_billing.billing.get_by_stripe_customer(
        db, stripe_customer_id=customer_id
    )
    
    if billing:
        # Could update customer info here if needed
        await db.commit()

