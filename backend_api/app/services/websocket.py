"""
WebSocket connection manager for real-time streaming
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    EXECUTE = "execute"
    CANCEL = "cancel"
    PING = "ping"
    
    # Server -> Client
    STREAM = "stream"
    COMPLETE = "complete"
    ERROR = "error"
    STATUS = "status"
    PONG = "pong"


@dataclass
class Connection:
    """Represents a WebSocket connection"""
    websocket: WebSocket
    user_id: UUID
    project_ids: Set[UUID] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    
    async def send_json(self, data: dict) -> bool:
        """Send JSON data to the connection"""
        try:
            await self.websocket.send_json(data)
            return True
        except Exception as e:
            logger.error(f"Error sending to {self.user_id}: {e}")
            return False


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # user_id -> Connection
        self._connections: Dict[str, Connection] = {}
        # project_id -> set of user_ids subscribed
        self._project_subscribers: Dict[str, Set[str]] = {}
        # For broadcasting to all
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: UUID) -> Connection:
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        user_key = str(user_id)
        
        async with self._lock:
            # Close existing connection if any
            if user_key in self._connections:
                try:
                    await self._connections[user_key].websocket.close()
                except:
                    pass
            
            connection = Connection(websocket=websocket, user_id=user_id)
            self._connections[user_key] = connection
        
        logger.info(f"User {user_id} connected via WebSocket")
        
        # Send welcome message
        await connection.send_json({
            "type": MessageType.STATUS.value,
            "data": {"status": "connected", "user_id": str(user_id)}
        })
        
        return connection
    
    async def disconnect(self, user_id: UUID):
        """Remove a WebSocket connection"""
        user_key = str(user_id)
        
        async with self._lock:
            if user_key in self._connections:
                connection = self._connections[user_key]
                
                # Unsubscribe from all projects
                for project_id in list(connection.project_ids):
                    project_key = str(project_id)
                    if project_key in self._project_subscribers:
                        self._project_subscribers[project_key].discard(user_key)
                
                del self._connections[user_key]
                logger.info(f"User {user_id} disconnected")
    
    async def subscribe_to_project(self, user_id: UUID, project_id: UUID):
        """Subscribe a user to project updates"""
        user_key = str(user_id)
        project_key = str(project_id)
        
        async with self._lock:
            if user_key in self._connections:
                self._connections[user_key].project_ids.add(project_id)
                
                if project_key not in self._project_subscribers:
                    self._project_subscribers[project_key] = set()
                self._project_subscribers[project_key].add(user_key)
                
                logger.info(f"User {user_id} subscribed to project {project_id}")
    
    async def unsubscribe_from_project(self, user_id: UUID, project_id: UUID):
        """Unsubscribe a user from project updates"""
        user_key = str(user_id)
        project_key = str(project_id)
        
        async with self._lock:
            if user_key in self._connections:
                self._connections[user_key].project_ids.discard(project_id)
            
            if project_key in self._project_subscribers:
                self._project_subscribers[project_key].discard(user_key)
    
    async def send_to_user(
        self, 
        user_id: UUID, 
        message_type: MessageType, 
        data: Any
    ) -> bool:
        """Send a message to a specific user"""
        user_key = str(user_id)
        
        if user_key in self._connections:
            return await self._connections[user_key].send_json({
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        return False
    
    async def broadcast_to_project(
        self, 
        project_id: UUID, 
        message_type: MessageType, 
        data: Any
    ):
        """Broadcast a message to all users subscribed to a project"""
        project_key = str(project_id)
        
        if project_key not in self._project_subscribers:
            return
        
        message = {
            "type": message_type.value,
            "data": data,
            "project_id": str(project_id),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_key in list(self._project_subscribers[project_key]):
            if user_key in self._connections:
                await self._connections[user_key].send_json(message)
    
    async def stream_to_user(
        self,
        user_id: UUID,
        project_id: UUID,
        content: str,
        chunk_type: str = "text"
    ):
        """Stream content chunk to user"""
        await self.send_to_user(user_id, MessageType.STREAM, {
            "project_id": str(project_id),
            "content": content,
            "chunk_type": chunk_type
        })
    
    async def send_completion(
        self,
        user_id: UUID,
        project_id: UUID,
        result: Any
    ):
        """Send completion message to user"""
        await self.send_to_user(user_id, MessageType.COMPLETE, {
            "project_id": str(project_id),
            "result": result
        })
    
    async def send_error(
        self,
        user_id: UUID,
        project_id: Optional[UUID],
        error: str,
        code: str = "UNKNOWN"
    ):
        """Send error message to user"""
        await self.send_to_user(user_id, MessageType.ERROR, {
            "project_id": str(project_id) if project_id else None,
            "error": error,
            "code": code
        })
    
    def get_active_connections(self) -> int:
        """Get number of active connections"""
        return len(self._connections)
    
    def get_project_subscribers(self, project_id: UUID) -> int:
        """Get number of subscribers for a project"""
        project_key = str(project_id)
        return len(self._project_subscribers.get(project_key, set()))


# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, user_id: UUID):
    """Main WebSocket handler for a connection"""
    connection = await manager.connect(websocket, user_id)
    
    try:
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type", "")
                payload = data.get("data", {})
                
                if message_type == MessageType.PING.value:
                    await connection.send_json({
                        "type": MessageType.PONG.value,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == MessageType.SUBSCRIBE.value:
                    project_id = payload.get("project_id")
                    if project_id:
                        await manager.subscribe_to_project(user_id, UUID(project_id))
                        await connection.send_json({
                            "type": MessageType.STATUS.value,
                            "data": {"subscribed": project_id}
                        })
                
                elif message_type == MessageType.UNSUBSCRIBE.value:
                    project_id = payload.get("project_id")
                    if project_id:
                        await manager.unsubscribe_from_project(user_id, UUID(project_id))
                        await connection.send_json({
                            "type": MessageType.STATUS.value,
                            "data": {"unsubscribed": project_id}
                        })
                
                elif message_type == MessageType.EXECUTE.value:
                    # Handle execute request (will be processed by multi-agent)
                    await connection.send_json({
                        "type": MessageType.STATUS.value,
                        "data": {"status": "execution_queued", **payload}
                    })
                
            except json.JSONDecodeError:
                await manager.send_error(user_id, None, "Invalid JSON", "INVALID_JSON")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await manager.disconnect(user_id)
