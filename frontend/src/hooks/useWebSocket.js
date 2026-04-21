import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

export const useWebSocket = (roomId) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!roomId) return;
    const token = localStorage.getItem('access_token');
    const newSocket = io(import.meta.env.VITE_WS_URL, {
      path: `/ws/chat/${roomId}/`,
      query: { token },
      transports: ['websocket'],
    });
    newSocket.on('connect', () => console.log('WebSocket connected'));
    newSocket.on('chat_message', (data) => setMessages((prev) => [...prev, data]));
    socketRef.current = newSocket;
    setSocket(newSocket);
    return () => newSocket.close();
  }, [roomId]);

  const sendMessage = (message) => {
    if (socketRef.current) socketRef.current.emit('chat_message', { message });
  };

  return { socket, messages, sendMessage, setMessages };
};