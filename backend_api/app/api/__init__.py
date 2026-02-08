"""API routes"""
from fastapi import APIRouter

from app.api import auth, users, teams, projects, billing, deployments, memory
from app.api import websocket, sandbox, visual_builder

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["Deployments"])
api_router.include_router(memory.router, prefix="/memory", tags=["Memory"])

# New advanced features
api_router.include_router(websocket.router, tags=["WebSocket"])
api_router.include_router(sandbox.router, tags=["Sandbox"])
api_router.include_router(visual_builder.router, tags=["Visual Builder"])

__all__ = ["api_router"]
