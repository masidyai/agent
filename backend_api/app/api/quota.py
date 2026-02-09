"""
Quota enforcement helpers and dependencies
"""
from functools import wraps
from typing import Callable
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.usage_tracking import usage_tracking


async def check_and_enforce_quota(
    db: AsyncSession,
    user_id: UUID,
    quota_type: str,
) -> None:
    """
    Check quota and raise HTTPException if exceeded
    
    Args:
        db: Database session
        user_id: User ID to check quota for
        quota_type: Type of quota to check (projects, executions, etc.)
    
    Raises:
        HTTPException: If quota is exceeded (429 Too Many Requests)
    """
    has_quota, message = await usage_tracking.check_quota(
        db, user_id=user_id, quota_type=quota_type
    )
    
    if not has_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
        )


def get_quota_error_detail(quota_type: str, current: int, limit: int) -> dict:
    """
    Generate a detailed error response for quota exceeded
    
    Returns:
        dict: Error details with upgrade suggestion
    """
    return {
        "error": "quota_exceeded",
        "quota_type": quota_type,
        "current": current,
        "limit": limit,
        "message": f"You've reached your {quota_type} limit ({current}/{limit}).",
        "upgrade_required": True,
        "upgrade_url": "/api/billing/plans",
    }
