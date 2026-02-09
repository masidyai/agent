"""
AI Trust Engine for risk evaluation
"""
from typing import Dict, Any, Optional


class RiskEvaluator:
    """Evaluates risk of actions using rule-based system"""
    
    # High-risk actions
    HIGH_RISK_ACTIONS = {
        "delete_account",
        "transfer_ownership",
        "revoke_key",
        "change_email",
        "disable_2fa",
        "export_data",
        "api_key_create",
    }
    
    # Medium-risk actions
    MEDIUM_RISK_ACTIONS = {
        "create_identity",
        "derive_key",
        "create_project",
        "deploy_project",
        "invite_member",
        "change_password",
    }
    
    @staticmethod
    def evaluate(
        action: str,
        actor_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Evaluate risk score for an action
        
        Args:
            action: Action being performed
            actor_type: Type of actor (user, system, ai_agent)
            context: Optional context information
            
        Returns:
            Risk score from 0.0 (safe) to 1.0 (dangerous)
        """
        base_score = 0.0
        
        # Check action risk level
        if action in RiskEvaluator.HIGH_RISK_ACTIONS:
            base_score = 0.8
        elif action in RiskEvaluator.MEDIUM_RISK_ACTIONS:
            base_score = 0.5
        else:
            base_score = 0.2
        
        # Adjust based on actor type
        if actor_type == "system":
            base_score *= 0.5  # System actions are generally safer
        elif actor_type == "ai_agent":
            base_score *= 1.2  # AI agent actions need more scrutiny
            base_score = min(base_score, 1.0)  # Cap at 1.0
        
        # Adjust based on context
        if context:
            # Check for suspicious patterns
            if context.get("failed_attempts", 0) > 3:
                base_score += 0.2
            
            # Check for unusual timing
            if context.get("unusual_time", False):
                base_score += 0.1
            
            # Check for new device/location
            if context.get("new_device", False):
                base_score += 0.15
            
            # Check for rapid successive actions
            if context.get("rapid_actions", False):
                base_score += 0.1
            
            # Cap at 1.0
            base_score = min(base_score, 1.0)
        
        return round(base_score, 2)
    
    @staticmethod
    def should_challenge(risk_score: float) -> bool:
        """
        Determine if action should require additional verification
        
        Args:
            risk_score: Risk score from evaluate()
            
        Returns:
            True if additional challenge is needed
        """
        return risk_score >= 0.7
    
    @staticmethod
    def should_deny(risk_score: float) -> bool:
        """
        Determine if action should be denied
        
        Args:
            risk_score: Risk score from evaluate()
            
        Returns:
            True if action should be denied
        """
        return risk_score >= 0.9
    
    @staticmethod
    def get_risk_level(risk_score: float) -> str:
        """
        Get risk level string from score
        
        Args:
            risk_score: Risk score from evaluate()
            
        Returns:
            Risk level: low, medium, or high
        """
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
