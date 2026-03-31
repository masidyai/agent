"""
Event logger service for chain-like audit logging
"""
import uuid
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chain.events.models import ChainEvent


class EventLogger:
    """Service for logging events in a chain-like structure"""
    
    @staticmethod
    def generate_event_id() -> str:
        """Generate a unique event ID"""
        return f"evt_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def calculate_hash(
        event_id: str,
        actor: str,
        action: str,
        target: Optional[str],
        timestamp: datetime,
        prev_hash: Optional[str] = None
    ) -> str:
        """
        Calculate SHA256 hash for event chaining
        
        Args:
            event_id: Event ID
            actor: Actor performing the action
            action: Action being performed
            target: Target of the action
            timestamp: Event timestamp
            prev_hash: Hash of previous event
            
        Returns:
            SHA256 hash hex digest
        """
        # Create deterministic string for hashing
        data = f"{event_id}:{actor}:{action}:{target or ''}:{timestamp.isoformat()}"
        if prev_hash:
            data = f"{prev_hash}:{data}"
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    async def get_last_event(db: AsyncSession) -> Optional[ChainEvent]:
        """
        Get the most recent event in the chain
        
        Args:
            db: Database session
            
        Returns:
            Last ChainEvent or None
        """
        result = await db.execute(
            select(ChainEvent).order_by(ChainEvent.timestamp.desc()).limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def log_event(
        db: AsyncSession,
        actor: str,
        actor_type: str,
        action: str,
        target: Optional[str] = None,
        target_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ai_risk_score: float = 0.0
    ) -> ChainEvent:
        """
        Log a new event in the chain
        
        Args:
            db: Database session
            actor: Actor performing the action
            actor_type: Type of actor (user, system, ai_agent)
            action: Action being performed
            target: Optional target of the action
            target_type: Optional type of target
            metadata: Optional metadata as dict
            ip_address: Optional IP address
            user_agent: Optional user agent
            ai_risk_score: AI-calculated risk score (0.0 to 1.0)
            
        Returns:
            Created ChainEvent
        """
        # Get previous event for chain linking
        prev_event = await EventLogger.get_last_event(db)
        prev_hash = prev_event.event_hash if prev_event else None
        
        # Generate event ID
        event_id = EventLogger.generate_event_id()
        timestamp = datetime.utcnow()
        
        # Calculate event hash
        event_hash = EventLogger.calculate_hash(
            event_id=event_id,
            actor=actor,
            action=action,
            target=target,
            timestamp=timestamp,
            prev_hash=prev_hash
        )
        
        # Determine risk level from score
        if ai_risk_score >= 0.7:
            risk_level = "high"
        elif ai_risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Create event
        event = ChainEvent(
            event_id=event_id,
            actor=actor,
            actor_type=actor_type,
            action=action,
            target=target,
            target_type=target_type,
            ai_risk_score=ai_risk_score,
            risk_level=risk_level,
            event_hash=event_hash,
            prev_hash=prev_hash,
            event_metadata=json.dumps(metadata) if metadata else None,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=timestamp,
        )
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        
        return event
    
    @staticmethod
    async def verify_chain(db: AsyncSession, limit: int = 100) -> bool:
        """
        Verify the integrity of the event chain
        
        Args:
            db: Database session
            limit: Number of recent events to verify
            
        Returns:
            True if chain is valid, False otherwise
        """
        result = await db.execute(
            select(ChainEvent).order_by(ChainEvent.timestamp.asc()).limit(limit)
        )
        events = result.scalars().all()
        
        if not events:
            return True
        
        # Verify each event's hash
        prev_hash = None
        for event in events:
            # Recalculate hash
            expected_hash = EventLogger.calculate_hash(
                event_id=event.event_id,
                actor=event.actor,
                action=event.action,
                target=event.target,
                timestamp=event.timestamp,
                prev_hash=prev_hash
            )
            
            # Check if hash matches
            if event.event_hash != expected_hash:
                return False
            
            # Check if prev_hash matches
            if event.prev_hash != prev_hash:
                return False
            
            prev_hash = event.event_hash
        
        return True
    
    @staticmethod
    async def get_events_by_actor(
        db: AsyncSession,
        actor: str,
        limit: int = 50
    ) -> list[ChainEvent]:
        """
        Get events by actor
        
        Args:
            db: Database session
            actor: Actor identifier
            limit: Maximum number of events to return
            
        Returns:
            List of ChainEvents
        """
        result = await db.execute(
            select(ChainEvent)
            .where(ChainEvent.actor == actor)
            .order_by(ChainEvent.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_high_risk_events(
        db: AsyncSession,
        threshold: float = 0.7,
        limit: int = 50
    ) -> list[ChainEvent]:
        """
        Get high-risk events
        
        Args:
            db: Database session
            threshold: Risk score threshold
            limit: Maximum number of events to return
            
        Returns:
            List of high-risk ChainEvents
        """
        result = await db.execute(
            select(ChainEvent)
            .where(ChainEvent.ai_risk_score >= threshold)
            .order_by(ChainEvent.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
