"""Tests for Masidy Chain - Identity and Key Vault"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.chain.identity.service import IdentityService
from app.chain.identity.key_vault import key_vault
from app.chain.events.service import EventLogger


class TestChainIdentity:
    """Test Masidy Chain identity endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_identity(self, auth_client: AsyncClient, test_db):
        """Test creating a new Masidy Identity"""
        response = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={
                "device_fingerprint": "test_device_123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "masidy_id" in data
        assert "identity" in data
        assert "root_key" in data
        
        # Check masidy_id format
        assert data["masidy_id"].startswith("masidy_")
        
        # Check identity data
        identity = data["identity"]
        assert identity["email"] == "test@example.com"
        assert identity["masidy_id"] == data["masidy_id"]
        assert identity["device_fingerprint"] == "test_device_123"
        
        # Check root key data
        root_key = data["root_key"]
        assert root_key["key_id"].startswith("root_")
        assert root_key["status"] == "active"
        assert root_key["masidy_id"] == data["masidy_id"]
    
    @pytest.mark.asyncio
    async def test_create_identity_duplicate(self, auth_client: AsyncClient):
        """Test that duplicate identity creation fails"""
        # Create first identity
        response1 = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        assert response1.status_code == 201
        
        # Try to create second identity (should fail)
        response2 = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_my_identity(self, auth_client: AsyncClient):
        """Test getting current user's identity"""
        # Create identity first
        create_response = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        assert create_response.status_code == 201
        created_data = create_response.json()
        
        # Get identity
        response = await auth_client.get("/api/v1/chain/identity/me")
        assert response.status_code == 200
        data = response.json()
        
        assert data["masidy_id"] == created_data["masidy_id"]
        assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_my_identity_not_found(self, auth_client: AsyncClient):
        """Test getting identity when none exists"""
        response = await auth_client.get("/api/v1/chain/identity/me")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_identity_by_id(self, auth_client: AsyncClient):
        """Test getting identity by masidy_id"""
        # Create identity
        create_response = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        assert create_response.status_code == 201
        masidy_id = create_response.json()["masidy_id"]
        
        # Get by ID
        response = await auth_client.get(f"/api/v1/chain/identity/{masidy_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["masidy_id"] == masidy_id
    
    @pytest.mark.asyncio
    async def test_derive_key(self, auth_client: AsyncClient):
        """Test deriving a scoped key"""
        # Create identity
        create_response = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        assert create_response.status_code == 201
        masidy_id = create_response.json()["masidy_id"]
        
        # Derive key
        response = await auth_client.post(
            "/api/v1/chain/identity/keys/derive",
            json={
                "masidy_id": masidy_id,
                "scope": "project",
                "scope_id": "test_project_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check derived key
        derived_key = data["derived_key"]
        assert derived_key["key_id"].startswith("derived_")
        assert derived_key["scope"] == "project"
        assert derived_key["scope_id"] == "test_project_123"
        assert derived_key["masidy_id"] == masidy_id
        assert "key_value" in derived_key  # Decrypted key should be included
    
    @pytest.mark.asyncio
    async def test_derive_key_idempotent(self, auth_client: AsyncClient):
        """Test that deriving same key twice returns the same key"""
        # Create identity
        create_response = await auth_client.post(
            "/api/v1/chain/identity/create",
            json={}
        )
        masidy_id = create_response.json()["masidy_id"]
        
        # Derive key first time
        response1 = await auth_client.post(
            "/api/v1/chain/identity/keys/derive",
            json={
                "masidy_id": masidy_id,
                "scope": "project",
                "scope_id": "test_project"
            }
        )
        key1 = response1.json()["derived_key"]
        
        # Derive key second time (same scope)
        response2 = await auth_client.post(
            "/api/v1/chain/identity/keys/derive",
            json={
                "masidy_id": masidy_id,
                "scope": "project",
                "scope_id": "test_project"
            }
        )
        key2 = response2.json()["derived_key"]
        
        # Should return the same key
        assert key1["key_id"] == key2["key_id"]
        assert key1["key_value"] == key2["key_value"]


class TestKeyVault:
    """Test KeyVault service"""
    
    def test_generate_root_key(self):
        """Test root key generation"""
        raw_key, encrypted_key = key_vault.generate_root_key()
        
        # Check format
        assert len(raw_key) > 0
        assert len(encrypted_key) > 0
        assert raw_key != encrypted_key
        
        # Check decryption
        decrypted = key_vault.decrypt_root_key(encrypted_key)
        assert decrypted == raw_key
    
    def test_derive_key(self):
        """Test key derivation"""
        # Generate root key
        root_key, _ = key_vault.generate_root_key()
        
        # Derive key
        derived1, encrypted1 = key_vault.derive_key(root_key, "project", "test1")
        
        # Derive again with same parameters (should be deterministic)
        derived2, encrypted2 = key_vault.derive_key(root_key, "project", "test1")
        
        assert derived1 == derived2
        
        # Derive with different scope_id (should be different)
        derived3, _ = key_vault.derive_key(root_key, "project", "test2")
        assert derived1 != derived3
    
    def test_generate_key_id(self):
        """Test key ID generation"""
        key_id1 = key_vault.generate_key_id("root")
        key_id2 = key_vault.generate_key_id("root")
        
        assert key_id1.startswith("root_")
        assert key_id2.startswith("root_")
        assert key_id1 != key_id2  # Should be unique


class TestEventLogger:
    """Test Event Logger service"""
    
    @pytest.mark.asyncio
    async def test_log_event(self, test_db):
        """Test logging an event"""
        async with test_db() as db:
            event = await EventLogger.log_event(
                db=db,
                actor="user_123",
                actor_type="user",
                action="create_identity",
                target="masidy_abc123",
                target_type="masidy_identity",
                ai_risk_score=0.3
            )
            
            assert event.event_id.startswith("evt_")
            assert event.actor == "user_123"
            assert event.action == "create_identity"
            assert event.ai_risk_score == 0.3
            assert event.risk_level == "low"
            assert len(event.event_hash) == 64  # SHA256 hash
            assert event.prev_hash is None  # First event
    
    @pytest.mark.asyncio
    async def test_event_chaining(self, test_db):
        """Test that events are properly chained"""
        async with test_db() as db:
            # Log first event
            event1 = await EventLogger.log_event(
                db=db,
                actor="user_123",
                actor_type="user",
                action="action1",
                ai_risk_score=0.2
            )
            
            # Log second event
            event2 = await EventLogger.log_event(
                db=db,
                actor="user_123",
                actor_type="user",
                action="action2",
                ai_risk_score=0.3
            )
            
            # Second event should reference first
            assert event1.prev_hash is None
            assert event2.prev_hash == event1.event_hash
    
    @pytest.mark.asyncio
    async def test_verify_chain(self, test_db):
        """Test chain verification"""
        async with test_db() as db:
            # Log multiple events
            for i in range(5):
                await EventLogger.log_event(
                    db=db,
                    actor=f"user_{i}",
                    actor_type="user",
                    action=f"action_{i}",
                    ai_risk_score=0.1 * i
                )
            
            # Verify chain
            is_valid = await EventLogger.verify_chain(db)
            assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_risk_levels(self, test_db):
        """Test risk level assignment"""
        async with test_db() as db:
            # Low risk
            event_low = await EventLogger.log_event(
                db=db,
                actor="user_1",
                actor_type="user",
                action="low_risk",
                ai_risk_score=0.2
            )
            assert event_low.risk_level == "low"
            
            # Medium risk
            event_medium = await EventLogger.log_event(
                db=db,
                actor="user_2",
                actor_type="user",
                action="medium_risk",
                ai_risk_score=0.5
            )
            assert event_medium.risk_level == "medium"
            
            # High risk
            event_high = await EventLogger.log_event(
                db=db,
                actor="user_3",
                actor_type="user",
                action="high_risk",
                ai_risk_score=0.8
            )
            assert event_high.risk_level == "high"


class TestAITrustEngine:
    """Test AI Trust Engine"""
    
    def test_risk_evaluation_high_risk_actions(self):
        """Test risk evaluation for high-risk actions"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        score = RiskEvaluator.evaluate("delete_account", "user")
        assert score >= 0.7  # Should be high risk
        
        score = RiskEvaluator.evaluate("revoke_key", "user")
        assert score >= 0.7
    
    def test_risk_evaluation_medium_risk_actions(self):
        """Test risk evaluation for medium-risk actions"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        score = RiskEvaluator.evaluate("create_identity", "user")
        assert 0.4 <= score < 0.7  # Should be medium risk
    
    def test_risk_evaluation_low_risk_actions(self):
        """Test risk evaluation for low-risk actions"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        score = RiskEvaluator.evaluate("view_profile", "user")
        assert score < 0.4  # Should be low risk
    
    def test_risk_evaluation_context(self):
        """Test risk evaluation with context"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        # Base score
        base_score = RiskEvaluator.evaluate("create_identity", "user")
        
        # With suspicious context
        high_score = RiskEvaluator.evaluate(
            "create_identity",
            "user",
            context={
                "failed_attempts": 5,
                "new_device": True,
                "unusual_time": True
            }
        )
        
        assert high_score > base_score
    
    def test_should_challenge(self):
        """Test challenge decision"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        assert RiskEvaluator.should_challenge(0.8) is True
        assert RiskEvaluator.should_challenge(0.5) is False
    
    def test_should_deny(self):
        """Test deny decision"""
        from app.chain.ai_trust.service import RiskEvaluator
        
        assert RiskEvaluator.should_deny(0.95) is True
        assert RiskEvaluator.should_deny(0.7) is False
