'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export type MessageType = 
  | 'subscribe' 
  | 'unsubscribe' 
  | 'execute' 
  | 'cancel' 
  | 'ping'
  | 'stream'
  | 'complete'
  | 'error'
  | 'status'
  | 'pong';

interface WebSocketMessage {
  type: MessageType;
  data?: any;
  project_id?: string;
  timestamp?: string;
}

interface UseWebSocketOptions {
  url?: string;
  token?: string;
  projectId?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onStream?: (content: string, chunkType: string) => void;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  onStatusChange?: (status: string) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  send: (type: MessageType, data?: any) => void;
  subscribe: (projectId: string) => void;
  unsubscribe: (projectId: string) => void;
  execute: (prompt: string, flow?: string) => void;
  cancel: (pipelineId: string) => void;
  disconnect: () => void;
  reconnect: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace(/^http/, 'ws');

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    token,
    projectId,
    onMessage,
    onStream,
    onComplete,
    onError,
    onStatusChange,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) return;

    setIsConnecting(true);
    clearTimers();

    const wsUrl = projectId 
      ? `${WS_URL}/api/v1/ws/project/${projectId}?token=${token}`
      : `${WS_URL}/api/v1/ws?token=${token}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      reconnectCountRef.current = 0;
      
      // Start ping interval
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        onMessage?.(message);
        
        switch (message.type) {
          case 'stream':
            onStream?.(message.data?.content, message.data?.chunk_type);
            break;
          case 'complete':
            onComplete?.(message.data?.result);
            break;
          case 'error':
            onError?.(message.data?.error);
            break;
          case 'status':
            onStatusChange?.(message.data?.status);
            break;
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setIsConnecting(false);
      clearTimers();

      // Attempt reconnection if not intentional close
      if (event.code !== 1000 && reconnectCountRef.current < reconnectAttempts) {
        reconnectCountRef.current++;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, reconnectInterval);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.('WebSocket connection error');
    };
  }, [token, projectId, onMessage, onStream, onComplete, onError, onStatusChange, reconnectAttempts, reconnectInterval, clearTimers]);

  const disconnect = useCallback(() => {
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close(1000, 'Intentional disconnect');
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
  }, [clearTimers]);

  const send = useCallback((type: MessageType, data?: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  const subscribe = useCallback((projectId: string) => {
    send('subscribe', { project_id: projectId });
  }, [send]);

  const unsubscribe = useCallback((projectId: string) => {
    send('unsubscribe', { project_id: projectId });
  }, [send]);

  const execute = useCallback((prompt: string, flow: string = 'saas') => {
    send('execute', { prompt, flow });
  }, [send]);

  const cancel = useCallback((pipelineId: string) => {
    send('cancel', { pipeline_id: pipelineId });
  }, [send]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectCountRef.current = 0;
    connect();
  }, [connect, disconnect]);

  useEffect(() => {
    if (token) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    send,
    subscribe,
    unsubscribe,
    execute,
    cancel,
    disconnect,
    reconnect,
  };
}
