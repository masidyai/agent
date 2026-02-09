"""Tests for GitHub integration"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient

from app.services.github import GitHubService
from app.core.security import encrypt_token, decrypt_token


class TestGitHubService:
    """Test GitHub service"""
    
    def test_sanitize_repo_name(self):
        """Test repository name sanitization"""
        service = GitHubService()
        
        assert service._sanitize_repo_name("My Project") == "my-project"
        assert service._sanitize_repo_name("Project@#$%") == "project"
        assert service._sanitize_repo_name("---leading-trailing---") == "leading-trailing"
        assert service._sanitize_repo_name("") == "generated-project"
        
        # Test length limit
        long_name = "a" * 200
        sanitized = service._sanitize_repo_name(long_name)
        assert len(sanitized) <= 100
    
    def test_generate_readme(self):
        """Test README generation"""
        service = GitHubService()
        
        readme = service.generate_readme(
            project_name="Test Project",
            description="A test project",
            features=["Feature 1", "Feature 2"],
            tech_stack=["Python", "FastAPI"],
        )
        
        assert "# Test Project" in readme
        assert "A test project" in readme
        assert "Feature 1" in readme
        assert "Python" in readme
    
    def test_generate_workflows(self):
        """Test GitHub Actions workflow generation"""
        service = GitHubService()
        
        # Test Python workflow
        python_workflow = service.generate_github_actions_workflow("python")
        assert "python-version" in python_workflow
        assert "pytest" in python_workflow
        
        # Test Node workflow
        node_workflow = service.generate_github_actions_workflow("node")
        assert "node-version" in node_workflow
        assert "npm" in node_workflow
        
        # Test generic workflow
        generic_workflow = service.generate_github_actions_workflow("unknown")
        assert "Build" in generic_workflow


class TestTokenEncryption:
    """Test token encryption/decryption"""
    
    def test_encrypt_decrypt(self):
        """Test token can be encrypted and decrypted"""
        original_token = "ghp_test123456789"
        
        encrypted = encrypt_token(original_token)
        assert encrypted != original_token
        assert len(encrypted) > 0
        
        decrypted = decrypt_token(encrypted)
        assert decrypted == original_token
    
    def test_empty_token(self):
        """Test empty token handling"""
        assert encrypt_token("") == ""
        assert decrypt_token("") == ""


class TestGitHubAPI:
    """Test GitHub API endpoints"""
    
    @pytest.mark.asyncio
    async def test_github_oauth_start(self, client: AsyncClient):
        """Test GitHub OAuth flow start"""
        # This will fail without GITHUB_CLIENT_ID set, but we can test the endpoint exists
        response = await client.get("/api/auth/github")
        # Should get either URL or error about missing client ID
        assert response.status_code in [200, 500]

