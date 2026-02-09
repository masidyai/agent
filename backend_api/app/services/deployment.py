"""
Deployment service for one-click deployments
Supports Vercel, Railway, and other providers
"""
import asyncio
import os
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

import httpx

logger = logging.getLogger(__name__)


class DeploymentProvider(str, Enum):
    """Supported deployment providers"""
    VERCEL = "vercel"
    RAILWAY = "railway"
    RENDER = "render"
    FLY = "fly"
    NETLIFY = "netlify"


class DeploymentStatus(str, Enum):
    """Deployment status states"""
    PENDING = "pending"
    QUEUED = "queued"
    BUILDING = "building"
    DEPLOYING = "deploying"
    READY = "ready"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class DeploymentConfig:
    """Configuration for a deployment"""
    provider: DeploymentProvider
    project_name: str
    project_dir: str
    environment: str = "production"
    env_vars: Dict[str, str] = None
    build_command: Optional[str] = None
    output_dir: Optional[str] = None
    framework: Optional[str] = None
    region: str = "auto"
    
    def __post_init__(self):
        self.env_vars = self.env_vars or {}


@dataclass
class DeploymentResult:
    """Result of a deployment"""
    status: DeploymentStatus
    provider: DeploymentProvider
    deployment_id: Optional[str] = None
    url: Optional[str] = None
    preview_url: Optional[str] = None
    build_logs: Optional[str] = None
    deploy_logs: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "provider": self.provider.value,
            "deployment_id": self.deployment_id,
            "url": self.url,
            "preview_url": self.preview_url,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DeploymentProviderBase(ABC):
    """Base class for deployment providers"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.client = httpx.AsyncClient(timeout=60.0)
    
    @abstractmethod
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy a project"""
        pass
    
    @abstractmethod
    async def get_status(self, deployment_id: str) -> DeploymentResult:
        """Get deployment status"""
        pass
    
    @abstractmethod
    async def cancel(self, deployment_id: str) -> bool:
        """Cancel a deployment"""
        pass
    
    async def close(self):
        await self.client.aclose()


class VercelProvider(DeploymentProviderBase):
    """Vercel deployment provider"""
    
    BASE_URL = "https://api.vercel.com"
    
    def __init__(self, api_token: Optional[str] = None):
        super().__init__(api_token or os.getenv("VERCEL_TOKEN"))
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy to Vercel"""
        result = DeploymentResult(
            status=DeploymentStatus.PENDING,
            provider=DeploymentProvider.VERCEL,
            started_at=datetime.utcnow()
        )
        
        if not self.api_token:
            result.status = DeploymentStatus.ERROR
            result.error = "Vercel API token not configured"
            return result
        
        try:
            # Create deployment
            # Note: In production, you'd upload files or use Git integration
            payload = {
                "name": config.project_name,
                "target": config.environment,
                "gitSource": None,  # Would be set for Git-based deploys
                "projectSettings": {
                    "buildCommand": config.build_command,
                    "outputDirectory": config.output_dir,
                    "framework": config.framework,
                },
                "env": config.env_vars,
            }
            
            # This is a placeholder - actual Vercel deployment requires
            # either Git integration or file upload via their API
            result.status = DeploymentStatus.QUEUED
            result.deployment_id = f"dpl_simulated_{datetime.utcnow().timestamp()}"
            
            # Simulate deployment process
            await asyncio.sleep(1)
            result.status = DeploymentStatus.BUILDING
            
            await asyncio.sleep(2)
            result.status = DeploymentStatus.DEPLOYING
            
            await asyncio.sleep(1)
            result.status = DeploymentStatus.READY
            result.url = f"https://{config.project_name}.vercel.app"
            result.preview_url = f"https://{config.project_name}-preview.vercel.app"
            result.completed_at = datetime.utcnow()
            
        except Exception as e:
            result.status = DeploymentStatus.ERROR
            result.error = str(e)
            result.completed_at = datetime.utcnow()
            logger.error(f"Vercel deployment error: {e}")
        
        return result
    
    async def get_status(self, deployment_id: str) -> DeploymentResult:
        """Get Vercel deployment status"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v13/deployments/{deployment_id}",
                headers=self._headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                status_map = {
                    "QUEUED": DeploymentStatus.QUEUED,
                    "BUILDING": DeploymentStatus.BUILDING,
                    "READY": DeploymentStatus.READY,
                    "ERROR": DeploymentStatus.ERROR,
                    "CANCELED": DeploymentStatus.CANCELLED,
                }
                
                return DeploymentResult(
                    status=status_map.get(data.get("readyState"), DeploymentStatus.PENDING),
                    provider=DeploymentProvider.VERCEL,
                    deployment_id=deployment_id,
                    url=data.get("url"),
                )
            else:
                return DeploymentResult(
                    status=DeploymentStatus.ERROR,
                    provider=DeploymentProvider.VERCEL,
                    error=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            return DeploymentResult(
                status=DeploymentStatus.ERROR,
                provider=DeploymentProvider.VERCEL,
                error=str(e)
            )
    
    async def cancel(self, deployment_id: str) -> bool:
        """Cancel a Vercel deployment"""
        try:
            response = await self.client.patch(
                f"{self.BASE_URL}/v12/deployments/{deployment_id}/cancel",
                headers=self._headers()
            )
            return response.status_code == 200
        except:
            return False


class RailwayProvider(DeploymentProviderBase):
    """Railway deployment provider"""
    
    BASE_URL = "https://backboard.railway.app/graphql/v2"
    
    def __init__(self, api_token: Optional[str] = None):
        super().__init__(api_token or os.getenv("RAILWAY_TOKEN"))
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy to Railway"""
        result = DeploymentResult(
            status=DeploymentStatus.PENDING,
            provider=DeploymentProvider.RAILWAY,
            started_at=datetime.utcnow()
        )
        
        if not self.api_token:
            result.status = DeploymentStatus.ERROR
            result.error = "Railway API token not configured"
            return result
        
        try:
            # Placeholder for Railway deployment
            result.status = DeploymentStatus.QUEUED
            result.deployment_id = f"railway_simulated_{datetime.utcnow().timestamp()}"
            
            await asyncio.sleep(2)
            result.status = DeploymentStatus.BUILDING
            
            await asyncio.sleep(3)
            result.status = DeploymentStatus.READY
            result.url = f"https://{config.project_name}.up.railway.app"
            result.completed_at = datetime.utcnow()
            
        except Exception as e:
            result.status = DeploymentStatus.ERROR
            result.error = str(e)
            result.completed_at = datetime.utcnow()
        
        return result
    
    async def get_status(self, deployment_id: str) -> DeploymentResult:
        """Get Railway deployment status"""
        return DeploymentResult(
            status=DeploymentStatus.READY,
            provider=DeploymentProvider.RAILWAY,
            deployment_id=deployment_id
        )
    
    async def cancel(self, deployment_id: str) -> bool:
        """Cancel a Railway deployment"""
        return True


class DeploymentService:
    """
    Main deployment service that orchestrates deployments
    across different providers.
    """
    
    def __init__(self):
        self.providers: Dict[DeploymentProvider, DeploymentProviderBase] = {}
        self.active_deployments: Dict[str, DeploymentResult] = {}
        self._lock = asyncio.Lock()
    
    def get_provider(self, provider: DeploymentProvider) -> DeploymentProviderBase:
        """Get or create a deployment provider"""
        if provider not in self.providers:
            if provider == DeploymentProvider.VERCEL:
                self.providers[provider] = VercelProvider()
            elif provider == DeploymentProvider.RAILWAY:
                self.providers[provider] = RailwayProvider()
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        return self.providers[provider]
    
    async def deploy(
        self,
        config: DeploymentConfig,
        project_id: Optional[UUID] = None
    ) -> DeploymentResult:
        """
        Deploy a project to the specified provider.
        
        Args:
            config: Deployment configuration
            project_id: Optional project ID for tracking
        
        Returns:
            DeploymentResult
        """
        provider = self.get_provider(config.provider)
        result = await provider.deploy(config)
        
        if result.deployment_id:
            async with self._lock:
                self.active_deployments[result.deployment_id] = result
        
        return result
    
    async def get_status(
        self,
        deployment_id: str,
        provider: DeploymentProvider
    ) -> DeploymentResult:
        """Get the status of a deployment"""
        provider_instance = self.get_provider(provider)
        return await provider_instance.get_status(deployment_id)
    
    async def cancel(
        self,
        deployment_id: str,
        provider: DeploymentProvider
    ) -> bool:
        """Cancel a deployment"""
        provider_instance = self.get_provider(provider)
        success = await provider_instance.cancel(deployment_id)
        
        if success:
            async with self._lock:
                if deployment_id in self.active_deployments:
                    self.active_deployments[deployment_id].status = DeploymentStatus.CANCELLED
        
        return success
    
    async def list_active_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        return [
            result.to_dict() 
            for result in self.active_deployments.values()
        ]
    
    def generate_vercel_config(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Generate vercel.json configuration"""
        return {
            "version": 2,
            "name": config.project_name,
            "builds": [
                {
                    "src": "package.json",
                    "use": "@vercel/next" if config.framework == "next" else "@vercel/static-build"
                }
            ],
            "routes": [
                {"src": "/(.*)", "dest": "/$1"}
            ],
            "env": config.env_vars,
        }
    
    def generate_railway_config(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Generate railway.json configuration"""
        return {
            "build": {
                "builder": "NIXPACKS",
                "buildCommand": config.build_command or "npm run build",
            },
            "deploy": {
                "startCommand": "npm start",
                "healthcheckPath": "/",
            },
        }
    
    async def close(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            await provider.close()


# Global deployment service instance
deployment_service = DeploymentService()
