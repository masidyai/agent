"""
Chain identity API router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.chain.identity.schemas import (
    CreateIdentityRequest,
    CreateIdentityResponse,
    MasidyIdentityResponse,
    RootKeyResponse,
    DeriveKeyRequest,
    DeriveKeyResponse,
    DerivedKeyResponse,
)
from app.chain.identity.service import IdentityService
from app.chain.identity.key_vault import key_vault
from app.chain.events.service import EventLogger
from app.chain.ai_trust.service import RiskEvaluator

router = APIRouter()


@router.post("/create", response_model=CreateIdentityResponse, status_code=status.HTTP_201_CREATED)
async def create_identity(
    request: CreateIdentityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    http_request: Request = None,
):
    """
    Create a new Masidy Identity for the current user
    """
    try:
        # Check if identity already exists
        existing = await IdentityService.get_identity_by_user(db, current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identity already exists for this user"
            )
        
        # Create identity
        identity, root_key = await IdentityService.create_identity(
            db=db,
            user=current_user,
            device_fingerprint=request.device_fingerprint
        )
        
        # Calculate risk score
        risk_score = RiskEvaluator.evaluate(
            action="create_identity",
            actor_type="user",
            context={"new_device": bool(request.device_fingerprint)}
        )
        
        # Log event
        await EventLogger.log_event(
            db=db,
            actor=str(current_user.id),
            actor_type="user",
            action="create_identity",
            target=identity.masidy_id,
            target_type="masidy_identity",
            metadata={
                "email": current_user.email,
                "device_fingerprint": request.device_fingerprint,
            },
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None,
            ai_risk_score=risk_score
        )
        
        return CreateIdentityResponse(
            masidy_id=identity.masidy_id,
            identity=MasidyIdentityResponse.model_validate(identity),
            root_key=RootKeyResponse.model_validate(root_key),
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=MasidyIdentityResponse)
async def get_my_identity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's Masidy Identity
    """
    identity = await IdentityService.get_identity_by_user(db, current_user.id)
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No identity found for current user"
        )
    
    return MasidyIdentityResponse.model_validate(identity)


@router.get("/{masidy_id}", response_model=MasidyIdentityResponse)
async def get_identity(
    masidy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Masidy Identity information
    """
    # Get identity
    identity = await IdentityService.get_identity(db, masidy_id)
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found"
        )
    
    # Check if user owns this identity
    if identity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this identity"
        )
    
    return MasidyIdentityResponse.model_validate(identity)


@router.post("/keys/derive", response_model=DeriveKeyResponse)
async def derive_key(
    request: DeriveKeyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    http_request: Request = None,
):
    """
    Derive a scoped key for a Masidy Identity
    """
    try:
        # Get identity
        identity = await IdentityService.get_identity(db, request.masidy_id)
        if not identity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identity not found"
            )
        
        # Check if user owns this identity
        if identity.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this identity"
            )
        
        # Derive key
        derived_key = await IdentityService.derive_key(
            db=db,
            masidy_id=request.masidy_id,
            scope=request.scope,
            scope_id=request.scope_id
        )
        
        # Calculate risk score
        risk_score = RiskEvaluator.evaluate(
            action="derive_key",
            actor_type="user",
            context={"scope": request.scope}
        )
        
        # Log event
        await EventLogger.log_event(
            db=db,
            actor=str(current_user.id),
            actor_type="user",
            action="derive_key",
            target=request.masidy_id,
            target_type="masidy_identity",
            metadata={
                "scope": request.scope,
                "scope_id": request.scope_id,
                "key_id": derived_key.key_id,
            },
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None,
            ai_risk_score=risk_score
        )
        
        # Decrypt the key for response (in production, this might be conditional)
        decrypted_key = key_vault.decrypt_derived_key(derived_key.encrypted_key)
        
        response_data = DerivedKeyResponse.model_validate(derived_key)
        response_data.key_value = decrypted_key  # Include decrypted key in response
        
        return DeriveKeyResponse(derived_key=response_data)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
