import React, { useState, useEffect, useRef } from 'react';
import { TextField, IconButton, Avatar, Typography } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useWebSocket } from '../../hooks/useWebSocket';
import { chatService } from '../../services/chat.service';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

export const ChatRoom = ({ roomId, currentUser }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const { sendMessage, messages: wsMessages } = useWebSocket(roomId);
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadMessages(); }, [roomId]);
  useEffect(() => { if (wsMessages.length) setMessages(prev => [...prev, wsMessages[wsMessages.length-1]]); }, [wsMessages]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const loadMessages = async () => {
    try {
      const room = await chatService.getRoom(roomId);
      setMessages(room.messages);
      await chatService.markMessagesAsRead(roomId);
    } finally { setLoading(false); }
  };

  if (loading) return <div className="flex justify-center items-center h-full text-blue">Загрузка...</div>;

  return (
    <div className="bg-white rounded-2xl shadow-lg flex flex-col h-full overflow-hidden">
      <div className="flex-grow overflow-y-auto p-4 space-y-3" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.user === currentUser.id ? 'justify-end' : 'justify-start'} animate-fade-up`}>
            <div className={`max-w-[70%] rounded-2xl p-3 ${msg.user === currentUser.id ? 'bg-gradient-primary text-white' : 'bg-gray-100 text-darkGray'}`}>
              <div className="flex items-center gap-2 mb-1">
                <Avatar src={msg.user_info.avatar || undefined} sx={{ width: 24, height: 24 }} />
                <Typography variant="caption" fontWeight="bold">{msg.user_info.first_name || msg.user_info.username}</Typography>
                <Typography variant="caption" fontSize="0.7rem" opacity={0.7}>{formatDistanceToNow(new Date(msg.created_at), { addSuffix: true, locale: ru })}</Typography>
              </div>
              <Typography variant="body2">{msg.message}</Typography>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t border-gray-100">
        <div className="flex gap-2">
          <TextField fullWidth variant="outlined" placeholder="Введите сообщение..." value={newMessage} onChange={(e) => setNewMessage(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage(newMessage)} size="small" sx={{ '& .MuiOutlinedInput-root': { borderRadius: '12px' } }} />
          <IconButton onClick={() => sendMessage(newMessage)} sx={{ background: 'linear-gradient(135deg, #37EBFF 0%, #0541F0 100%)', color: 'white', borderRadius: '12px' }}><SendIcon /></IconButton>
        </div>
      </div>
    </div>
  );
};