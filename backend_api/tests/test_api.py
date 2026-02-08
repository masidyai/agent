"""Tests for API endpoints"""
import pytest
from httpx import AsyncClient


class TestHealth:
    """Test health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Masidy API"
    
    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient):
        """Test health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]


class TestAuth:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register(self, client: AsyncClient):
        """Test user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "name": "New User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test duplicate email registration fails"""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "name": "User 1"
            }
        )
        
        # Duplicate registration
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "name": "User 2"
            }
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login(self, client: AsyncClient):
        """Test user login"""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "password123",
                "name": "Login User"
            }
        )
        
        # Login
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "login@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password fails"""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "password123",
                "name": "Wrong Pass User"
            }
        )
        
        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_me(self, auth_client: AsyncClient):
        """Test get current user"""
        response = await auth_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"


class TestBilling:
    """Test billing endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_plans(self, client: AsyncClient):
        """Test get billing plans"""
        response = await client.get("/api/v1/billing/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "free" in data["plans"]
        assert "pro" in data["plans"]
        assert "team" in data["plans"]
        assert "enterprise" in data["plans"]
    
    @pytest.mark.asyncio
    async def test_plan_details(self, client: AsyncClient):
        """Test plan details are correct"""
        response = await client.get("/api/v1/billing/plans")
        data = response.json()
        
        free_plan = data["plans"]["free"]
        assert free_plan["projects"] == 3
        assert free_plan["price_monthly"] == 0
        
        pro_plan = data["plans"]["pro"]
        assert pro_plan["projects"] == 25
        assert pro_plan["price_monthly"] == 19


class TestProjects:
    """Test project endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_project(self, auth_client: AsyncClient):
        """Test create project"""
        response = await auth_client.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "description": "A test project",
                "flow": "saas"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["flow"] == "saas"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_list_projects(self, auth_client: AsyncClient):
        """Test list projects"""
        # Create a project first
        await auth_client.post(
            "/api/v1/projects/",
            json={"name": "List Test Project"}
        )
        
        response = await auth_client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized project access fails"""
        response = await client.get("/api/v1/projects/")
        assert response.status_code == 401


class TestVisualBuilder:
    """Test visual builder endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_components(self, client: AsyncClient):
        """Test get visual builder components"""
        response = await client.get("/api/v1/visual-builder/components")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check component structure
        component = data[0]
        assert "id" in component
        assert "name" in component
        assert "category" in component
        assert "properties" in component
    
    @pytest.mark.asyncio
    async def test_get_templates(self, client: AsyncClient):
        """Test get visual builder templates"""
        response = await client.get("/api/v1/visual-builder/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) > 0


class TestWebSocket:
    """Test WebSocket endpoints"""
    
    @pytest.mark.asyncio
    async def test_ws_stats(self, client: AsyncClient):
        """Test WebSocket stats endpoint"""
        response = await client.get("/api/v1/ws/stats")
        assert response.status_code == 200
        data = response.json()
        assert "active_connections" in data
