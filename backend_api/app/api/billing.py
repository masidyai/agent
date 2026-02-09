"""
Billing API routes
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.crud import billing as crud_billing
from app.crud.billing import PLAN_LIMITS
from app.schemas.billing import (
    BillingResponse,
    UsageResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    PlanLimits,
    PlansResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.billing import BillingPlan

router = APIRouter()


@router.get("/", response_model=BillingResponse)
async def get_billing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's billing information"""
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.create_for_user(db, user_id=current_user.id)
    return billing


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current usage statistics"""
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.create_for_user(db, user_id=current_user.id)
    
    return UsageResponse(
        projects=billing.usage_projects,
        executions=billing.usage_executions,
        deployments=billing.usage_deployments,
        api_calls=billing.usage_api_calls,
        limits={
            "projects": billing.limit_projects,
            "executions": billing.limit_executions,
            "deployments": billing.limit_deployments,
        },
    )


@router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """Get available billing plans"""
    plans = {
        "free": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.FREE]["projects"],
            executions=PLAN_LIMITS[BillingPlan.FREE]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.FREE]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.FREE]["team_members"],
            price_monthly=0,
            price_yearly=0,
            features=[
                "3 projects",
                "10 executions/month",
                "1 deployment",
                "Community support",
            ],
        ),
        "pro": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.PRO]["projects"],
            executions=PLAN_LIMITS[BillingPlan.PRO]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.PRO]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.PRO]["team_members"],
            price_monthly=19,
            price_yearly=190,
            features=[
                "25 projects",
                "100 executions/month",
                "5 deployments",
                "Priority support",
                "Custom domains",
            ],
        ),
        "team": PlanLimits(
            projects=PLAN_LIMITS[BillingPlan.TEAM]["projects"],
            executions=PLAN_LIMITS[BillingPlan.TEAM]["executions"],
            deployments=PLAN_LIMITS[BillingPlan.TEAM]["deployments"],
            team_members=PLAN_LIMITS[BillingPlan.TEAM]["team_members"],
            price_monthly=49,
            price_yearly=490,
            features=[
                "100 projects",
                "500 executions/month",
                "20 deployments",
                "10 team members",
                "Team collaboration",
                "Admin controls",
                "Priority support",
            ],
        ),
        "enterprise": PlanLimits(
            projects=-1,
            executions=-1,
            deployments=-1,
            team_members=-1,
            price_monthly=0,  # Custom pricing
            price_yearly=0,
            features=[
                "Unlimited projects",
                "Unlimited executions",
                "Unlimited deployments",
                "Unlimited team members",
                "SSO/SAML",
                "Dedicated support",
                "Custom integrations",
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
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
    if not billing:
        billing = await crud_billing.create_for_user(db, user_id=current_user.id)
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Create or get Stripe customer
        if not billing.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                metadata={"user_id": str(current_user.id)},
            )
            await crud_billing.update_stripe_info(
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
    
    billing = await crud_billing.get_by_user(db, user_id=current_user.id)
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
):
    """Handle Stripe webhooks (called by Stripe)"""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook secret not configured",
        )
    
    # Get the raw body and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header",
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
    except ValueError:
        # Invalid payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe library not installed",
        )
    
    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]
    
    try:
        if event_type == "checkout.session.completed":
            # Payment successful, activate subscription
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")
            
            billing = await crud_billing.get_by_stripe_customer(
                db, stripe_customer_id=customer_id
            )
            if billing:
                # Update subscription info
                await crud_billing.update_stripe_info(
                    db,
                    billing=billing,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                )
                await db.commit()
        
        elif event_type == "customer.subscription.created":
            # New subscription created
            customer_id = data.get("customer")
            subscription_id = data.get("id")
            price_id = data["items"]["data"][0]["price"]["id"]
            
            billing = await crud_billing.get_by_stripe_customer(
                db, stripe_customer_id=customer_id
            )
            if billing:
                # Determine plan from price ID
                plan = BillingPlan.FREE
                if price_id == settings.STRIPE_PRICE_ID_PRO:
                    plan = BillingPlan.PRO
                elif price_id == settings.STRIPE_PRICE_ID_TEAM:
                    plan = BillingPlan.TEAM
                
                # Update subscription info and plan
                await crud_billing.update_stripe_info(
                    db,
                    billing=billing,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    stripe_price_id=price_id,
                )
                await crud_billing.update_plan(db, billing=billing, plan=plan)
                
                # Set billing period
                from app.models.billing import BillingStatus
                billing.status = BillingStatus.ACTIVE
                billing.current_period_start = datetime.fromtimestamp(data["current_period_start"])
                billing.current_period_end = datetime.fromtimestamp(data["current_period_end"])
                db.add(billing)
                await db.commit()
        
        elif event_type == "customer.subscription.updated":
            # Subscription updated (plan change, renewal, etc.)
            subscription_id = data.get("id")
            price_id = data["items"]["data"][0]["price"]["id"]
            
            billing = await crud_billing.get_by_stripe_subscription(
                db, stripe_subscription_id=subscription_id
            )
            if billing:
                # Determine plan from price ID
                plan = BillingPlan.FREE
                if price_id == settings.STRIPE_PRICE_ID_PRO:
                    plan = BillingPlan.PRO
                elif price_id == settings.STRIPE_PRICE_ID_TEAM:
                    plan = BillingPlan.TEAM
                
                await crud_billing.update_plan(db, billing=billing, plan=plan)
                
                # Update billing period and status
                from app.models.billing import BillingStatus
                billing.status = BillingStatus.ACTIVE
                billing.current_period_start = datetime.fromtimestamp(data["current_period_start"])
                billing.current_period_end = datetime.fromtimestamp(data["current_period_end"])
                db.add(billing)
                await db.commit()
        
        elif event_type == "customer.subscription.deleted":
            # Subscription canceled
            subscription_id = data.get("id")
            
            billing = await crud_billing.get_by_stripe_subscription(
                db, stripe_subscription_id=subscription_id
            )
            if billing:
                # Downgrade to free plan
                from app.models.billing import BillingStatus
                await crud_billing.update_plan(db, billing=billing, plan=BillingPlan.FREE)
                billing.status = BillingStatus.CANCELED
                billing.stripe_subscription_id = None
                billing.stripe_price_id = None
                db.add(billing)
                await db.commit()
        
        elif event_type == "invoice.payment_failed":
            # Payment failed
            customer_id = data.get("customer")
            
            billing = await crud_billing.get_by_stripe_customer(
                db, stripe_customer_id=customer_id
            )
            if billing:
                from app.models.billing import BillingStatus
                billing.status = BillingStatus.PAST_DUE
                db.add(billing)
                await db.commit()
        
        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded (renewal, etc.)
            customer_id = data.get("customer")
            
            billing = await crud_billing.get_by_stripe_customer(
                db, stripe_customer_id=customer_id
            )
            if billing:
                from app.models.billing import BillingStatus
                billing.status = BillingStatus.ACTIVE
                # Reset usage counters for new billing period
                await crud_billing.reset_usage(db, billing=billing)
                await db.commit()
    
    except Exception as e:
        # Log error but return 200 to prevent Stripe retries
        print(f"Error processing webhook: {str(e)}")
        return {"received": True, "error": str(e)}
    
    return {"received": True}
