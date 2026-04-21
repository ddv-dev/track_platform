import React, { useEffect, useState } from 'react';
import { Container, Paper, List, ListItem, ListItemText, Typography, CircularProgress } from '@mui/material';
import { chatService } from '../services/chat.service';
import { ChatRoom } from '../components/chat/ChatRoom';
import { useAuth } from '../hooks/useAuth';

export const ChatPage = () => {
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => { loadRooms(); }, []);

  const loadRooms = async () => {
    try { const data = await chatService.getRooms(); setRooms(data); } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  if (loading) return <div className="flex justify-center mt-8"><CircularProgress /></div>;

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6 text-darkBlue">Чаты с кураторами</Typography>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Paper className="h-[600px] overflow-y-auto">
          <List>
            {rooms.map((room) => (
              <ListItem button key={room.id} selected={selectedRoom?.id === room.id} onClick={() => setSelectedRoom(room)}>
                <ListItemText primary={`Трек #${room.track}`} secondary={room.last_message?.message?.slice(0, 50)} />
              </ListItem>
            ))}
            {rooms.length === 0 && <ListItem><ListItemText primary="Нет активных чатов" /></ListItem>}
          </List>
        </Paper>
        <div className="md:col-span-2 h-[600px]">
          {selectedRoom ? <ChatRoom roomId={selectedRoom.id} currentUser={user} /> : <Paper className="h-full flex items-center justify-center"><Typography color="textSecondary">Выберите чат</Typography></Paper>}
        </div>
      </div>
    </Container>
  );
};