"""
WebSocket API endpoints for real-time communication
"""
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

from app.services.websocket import manager, handle_websocket, MessageType
from app.services.multi_agent import orchestrator, AgentRole
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


async def get_user_from_token(token: str) -> UUID:
    """Validate token and return user ID"""
    payload = decode_token(token)
    if not payload:
        raise ValueError("Invalid token")
    return UUID(payload.get("sub"))


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    Main WebSocket endpoint for real-time communication.
    
    Connect with: ws://host/api/v1/ws?token=<jwt_token>
    
    Message types:
    - subscribe: Subscribe to project updates {"type": "subscribe", "data": {"project_id": "..."}}
    - unsubscribe: Unsubscribe from project {"type": "unsubscribe", "data": {"project_id": "..."}}
    - execute: Request AI execution {"type": "execute", "data": {"project_id": "...", "prompt": "..."}}
    - ping: Keep-alive {"type": "ping"}
    """
    try:
        user_id = await get_user_from_token(token)
    except Exception as e:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await handle_websocket(websocket, user_id)


@router.websocket("/ws/project/{project_id}")
async def project_websocket(
    websocket: WebSocket,
    project_id: UUID,
    token: str = Query(...)
):
    """
    Project-specific WebSocket for build streaming.
    
    Automatically subscribes to the project on connect.
    """
    try:
        user_id = await get_user_from_token(token)
    except Exception as e:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    connection = await manager.connect(websocket, user_id)
    await manager.subscribe_to_project(user_id, project_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "")
            payload = data.get("data", {})
            
            if message_type == "execute":
                # Execute build with multi-agent
                prompt = payload.get("prompt", "")
                flow = payload.get("flow", "saas")
                
                await manager.stream_to_user(
                    user_id, 
                    project_id,
                    "Starting build pipeline...",
                    "status"
                )
                
                # Create and execute pipeline
                pipeline = await orchestrator.create_pipeline(
                    project_id=project_id,
                    prompt=prompt,
                    flow=flow
                )
                
                async def stream_callback(role: str, content: str):
                    await manager.stream_to_user(
                        user_id,
                        project_id,
                        f"[{role}] {content}",
                        "agent"
                    )
                
                result = await orchestrator.execute_pipeline(
                    pipeline,
                    stream_callback
                )
                
                await manager.send_completion(user_id, project_id, result)
            
            elif message_type == "cancel":
                pipeline_id = payload.get("pipeline_id")
                if pipeline_id:
                    await orchestrator.cancel_pipeline(pipeline_id)
                    await connection.send_json({
                        "type": MessageType.STATUS.value,
                        "data": {"cancelled": pipeline_id}
                    })
            
            elif message_type == "ping":
                await connection.send_json({
                    "type": MessageType.PONG.value
                })
                
    except WebSocketDisconnect:
        logger.info(f"Project WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.error(f"Project WebSocket error: {e}")
        await manager.send_error(user_id, project_id, str(e))
    finally:
        await manager.unsubscribe_from_project(user_id, project_id)
        await manager.disconnect(user_id)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": manager.get_active_connections(),
    }
