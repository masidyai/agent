"""
Usage tracking service for billing and quota enforcement
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import billing as crud_billing
from app.crud.billing import usage_log as crud_usage_log, PRICING_CONFIG
from app.models.billing import UsageType


class UsageTrackingService:
    """Service for tracking usage and enforcing quotas"""
    
    @staticmethod
    def calculate_openai_cost(tokens: int) -> float:
        """Calculate OpenAI API cost based on token count"""
        cost_per_1k = PRICING_CONFIG["openai_cost_per_1k_tokens"]
        base_cost = (tokens / 1000) * cost_per_1k
        markup = PRICING_CONFIG["platform_markup_percent"] / 100
        return base_cost * (1 + markup)
    
    @staticmethod
    def calculate_docker_cost(minutes: float) -> float:
        """Calculate Docker execution cost based on minutes"""
        cost_per_minute = PRICING_CONFIG["docker_cost_per_minute"]
        base_cost = minutes * cost_per_minute
        markup = PRICING_CONFIG["platform_markup_percent"] / 100
        return base_cost * (1 + markup)
    
    @staticmethod
    def calculate_github_cost(repo_count: int) -> float:
        """Calculate GitHub storage cost based on repo count"""
        cost_per_repo = PRICING_CONFIG["github_storage_per_repo"]
        base_cost = repo_count * cost_per_repo
        markup = PRICING_CONFIG["platform_markup_percent"] / 100
        return base_cost * (1 + markup)
    
    async def log_openai_usage(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        tokens: int,
        model: str = "gpt-4",
        metadata: Optional[dict] = None,
    ) -> None:
        """Log OpenAI API usage and update billing"""
        cost = self.calculate_openai_cost(tokens)
        
        # Create usage log
        log_metadata = metadata or {}
        log_metadata["model"] = model
        log_metadata["tokens"] = tokens
        
        await crud_usage_log.create_log(
            db,
            user_id=user_id,
            usage_type=UsageType.OPENAI_CALL,
            quantity=tokens,
            cost=cost,
            metadata=log_metadata,
        )
        
        # Update billing
        billing = await crud_billing.billing.get_by_user(db, user_id=user_id)
        if billing:
            await crud_billing.billing.increment_usage(
                db, billing=billing, api_calls=1
            )
            await crud_billing.billing.add_cost(
                db, billing=billing, openai_cost=cost
            )
    
    async def log_docker_usage(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        minutes: float,
        metadata: Optional[dict] = None,
    ) -> None:
        """Log Docker execution usage and update billing"""
        cost = self.calculate_docker_cost(minutes)
        
        # Create usage log
        log_metadata = metadata or {}
        log_metadata["duration_minutes"] = minutes
        
        await crud_usage_log.create_log(
            db,
            user_id=user_id,
            usage_type=UsageType.DOCKER_EXEC,
            quantity=int(minutes * 60),  # Convert to seconds for quantity
            cost=cost,
            metadata=log_metadata,
        )
        
        # Update billing
        billing = await crud_billing.billing.get_by_user(db, user_id=user_id)
        if billing:
            await crud_billing.billing.increment_usage(
                db, billing=billing, executions=1
            )
            await crud_billing.billing.add_cost(
                db, billing=billing, docker_cost=cost
            )
    
    async def log_github_repo_creation(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        repo_name: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Log GitHub repo creation"""
        cost = self.calculate_github_cost(1)
        
        # Create usage log
        log_metadata = metadata or {}
        log_metadata["repo_name"] = repo_name
        
        await crud_usage_log.create_log(
            db,
            user_id=user_id,
            usage_type=UsageType.GITHUB_REPO,
            quantity=1,
            cost=cost,
            metadata=log_metadata,
        )
        
        # Update billing
        billing = await crud_billing.billing.get_by_user(db, user_id=user_id)
        if billing:
            await crud_billing.billing.increment_usage(
                db, billing=billing, github_repos=1
            )
    
    async def log_project_creation(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        project_id: UUID,
        metadata: Optional[dict] = None,
    ) -> None:
        """Log project creation"""
        # Create usage log
        log_metadata = metadata or {}
        log_metadata["project_id"] = str(project_id)
        
        await crud_usage_log.create_log(
            db,
            user_id=user_id,
            usage_type=UsageType.PROJECT_CREATE,
            quantity=1,
            cost=0.0,  # No direct cost, but counts toward quota
            metadata=log_metadata,
        )
        
        # Update billing
        billing = await crud_billing.billing.get_by_user(db, user_id=user_id)
        if billing:
            await crud_billing.billing.increment_usage(
                db, billing=billing, projects=1
            )
    
    async def check_quota(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        quota_type: str,
    ) -> tuple[bool, str]:
        """
        Check if user has quota available
        Returns: (has_quota, error_message)
        """
        is_ok, current, limit = await crud_billing.billing.check_limit(
            db, user_id=user_id, limit_type=quota_type
        )
        
        if not is_ok:
            if limit == 0:
                return False, "Your trial has expired. Please upgrade to continue."
            elif limit == -1:
                return True, ""
            else:
                return False, (
                    f"You've reached your {quota_type} limit ({current}/{limit}). "
                    f"Please upgrade to continue."
                )
        
        # Warning at 80% usage
        if limit != -1 and current >= limit * 0.8:
            warning = (
                f"Warning: You're at {current}/{limit} {quota_type} "
                f"({int((current/limit)*100)}% of your quota)."
            )
            return True, warning
        
        return True, ""
    
    async def get_upgrade_suggestion(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
    ) -> Optional[str]:
        """Get upgrade suggestion for user"""
        billing = await crud_billing.billing.get_by_user(db, user_id=user_id)
        if not billing:
            return None
        
        from app.models.billing import BillingPlan
        
        if billing.plan == BillingPlan.FREE:
            return "pro"
        elif billing.plan == BillingPlan.PRO:
            return "team"
        elif billing.plan == BillingPlan.TEAM:
            return "enterprise"
        
        return None


# Singleton instance
usage_tracking = UsageTrackingService()
