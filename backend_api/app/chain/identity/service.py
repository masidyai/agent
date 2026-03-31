"""
Identity service for managing Masidy identities and keys
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chain.identity.models import MasidyIdentity, RootKey, DerivedKey, KeyStatus
from app.chain.identity.key_vault import key_vault
from app.models.user import User


class IdentityService:
    """Service for managing Masidy identities"""
    
    @staticmethod
    def generate_masidy_id(user_id: uuid.UUID) -> str:
        """
        Generate a unique Masidy ID
        
        Args:
            user_id: User's UUID
            
        Returns:
            Masidy ID in format: masidy_<hash>
        """
        # Create a deterministic but unique ID based on user_id and timestamp
        data = f"{user_id}:{datetime.utcnow().isoformat()}"
        hash_value = key_vault.hash_data(data)[:16]
        return f"masidy_{hash_value}"
    
    @staticmethod
    async def create_identity(
        db: AsyncSession,
        user: User,
        device_fingerprint: Optional[str] = None
    ) -> tuple[MasidyIdentity, RootKey]:
        """
        Create a new Masidy Identity with root key
        
        Args:
            db: Database session
            user: User object
            device_fingerprint: Optional device fingerprint
            
        Returns:
            tuple: (MasidyIdentity, RootKey)
        """
        # Check if identity already exists
        result = await db.execute(
            select(MasidyIdentity).where(MasidyIdentity.user_id == user.id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Identity already exists for user {user.id}")
        
        # Generate Masidy ID
        masidy_id = IdentityService.generate_masidy_id(user.id)
        
        # Create identity
        identity = MasidyIdentity(
            masidy_id=masidy_id,
            user_id=user.id,
            email=user.email,
            device_fingerprint=device_fingerprint,
        )
        db.add(identity)
        await db.flush()  # Flush to get the ID
        
        # Generate root key
        raw_key, encrypted_key = key_vault.generate_root_key()
        root_key = RootKey(
            key_id=key_vault.generate_key_id("root"),
            masidy_id=masidy_id,
            encrypted_key=encrypted_key,
            status=KeyStatus.ACTIVE,
        )
        db.add(root_key)
        
        # Update identity with root key ID
        identity.root_key_id = root_key.id
        
        await db.commit()
        await db.refresh(identity)
        await db.refresh(root_key)
        
        return identity, root_key
    
    @staticmethod
    async def get_identity(
        db: AsyncSession,
        masidy_id: str
    ) -> Optional[MasidyIdentity]:
        """
        Get identity by Masidy ID
        
        Args:
            db: Database session
            masidy_id: Masidy ID
            
        Returns:
            MasidyIdentity or None
        """
        result = await db.execute(
            select(MasidyIdentity).where(MasidyIdentity.masidy_id == masidy_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_identity_by_user(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[MasidyIdentity]:
        """
        Get identity by user ID
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            MasidyIdentity or None
        """
        result = await db.execute(
            select(MasidyIdentity).where(MasidyIdentity.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def derive_key(
        db: AsyncSession,
        masidy_id: str,
        scope: str,
        scope_id: Optional[str] = None
    ) -> DerivedKey:
        """
        Derive a scoped key for a Masidy Identity
        
        Args:
            db: Database session
            masidy_id: Masidy ID
            scope: Scope of the key
            scope_id: Optional scope ID
            
        Returns:
            DerivedKey
        """
        # Check if derived key already exists
        query = select(DerivedKey).where(
            DerivedKey.masidy_id == masidy_id,
            DerivedKey.scope == scope
        )
        if scope_id:
            query = query.where(DerivedKey.scope_id == scope_id)
        
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            # Update last_used_at
            existing.last_used_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing)
            return existing
        
        # Get active root key
        result = await db.execute(
            select(RootKey).where(
                RootKey.masidy_id == masidy_id,
                RootKey.status == KeyStatus.ACTIVE
            ).order_by(RootKey.created_at.desc())
        )
        root_key = result.scalar_one_or_none()
        if not root_key:
            raise ValueError(f"No active root key found for {masidy_id}")
        
        # Decrypt root key
        decrypted_root = key_vault.decrypt_root_key(root_key.encrypted_key)
        
        # Derive new key
        derived_key_value, encrypted_derived = key_vault.derive_key(
            decrypted_root, scope, scope_id
        )
        
        # Store derived key
        derived_key = DerivedKey(
            key_id=key_vault.generate_key_id("derived"),
            masidy_id=masidy_id,
            scope=scope,
            scope_id=scope_id,
            encrypted_key=encrypted_derived,
            last_used_at=datetime.utcnow(),
        )
        db.add(derived_key)
        await db.commit()
        await db.refresh(derived_key)
        
        return derived_key
    
    @staticmethod
    async def get_active_root_key(
        db: AsyncSession,
        masidy_id: str
    ) -> Optional[RootKey]:
        """
        Get the active root key for a Masidy Identity
        
        Args:
            db: Database session
            masidy_id: Masidy ID
            
        Returns:
            RootKey or None
        """
        result = await db.execute(
            select(RootKey).where(
                RootKey.masidy_id == masidy_id,
                RootKey.status == KeyStatus.ACTIVE
            ).order_by(RootKey.created_at.desc())
        )
        return result.scalar_one_or_none()
