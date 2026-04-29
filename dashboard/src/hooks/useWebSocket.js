import { useState, useEffect, useRef, useCallback } from 'react';

const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY_MS = 3000;
const HISTORY_LIMIT = 100;

export const useWebSocket = (sessionId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [latestEvent, setLatestEvent] = useState(null);
  const [eventHistory, setEventHistory] = useState([]);
  
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeoutId = useRef(null);

  const connect = useCallback(() => {
    if (!sessionId) return;
    
    // Check if WS is already active
    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const socket = new WebSocket(`${wsUrl}/ws/${sessionId}`);
    
    socket.onopen = () => {
      console.log(`WebSocket connected for session: ${sessionId}`);
      setIsConnected(true);
      reconnectAttempts.current = 0; // reset attempts on success
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLatestEvent(data);
        setEventHistory((prev) => {
          const newHistory = [data, ...prev];
          if (newHistory.length > HISTORY_LIMIT) {
            return newHistory.slice(0, HISTORY_LIMIT);
          }
          return newHistory;
        });
      } catch (err) {
        console.error("Failed to parse WS payload:", err);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected.');
      
      // Auto reconnect
      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS && !!sessionId) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`);
        reconnectTimeoutId.current = setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      // Let onclose handle the reconnection
      socket.close();
    };

    ws.current = socket;
  }, [sessionId]);

  useEffect(() => {
    if (sessionId) {
      connect();
    }

    return () => {
      if (reconnectTimeoutId.current) clearTimeout(reconnectTimeoutId.current);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [sessionId, connect]);

  return { isConnected, latestEvent, eventHistory };
};
