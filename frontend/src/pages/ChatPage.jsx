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

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      const data = await chatService.getRooms();

      // --- Логика безопасного извлечения массива комнат ---
      let roomsArray = [];
      if (Array.isArray(data)) {
        roomsArray = data; // Это массив
      } else if (data?.results && Array.isArray(data.results)) {
        roomsArray = data.results; // Это объект с пагинацией
      } else if (data && typeof data === 'object') {
        // Если это объект, но не массив, возможно, это одна комната
        roomsArray = [data];
      }
      // ---------------------------------------------------

      setRooms(roomsArray);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="py-8">
        <div className="flex justify-center">
          <CircularProgress sx={{ color: '#0541F0' }} />
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6 text-darkBlue font-bold">
        Чаты с кураторами
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Список комнат */}
        <Paper className="h-[600px] overflow-y-auto">
          <List>
            {rooms.map((room) => (
              <ListItem
                button
                key={room.id}
                selected={selectedRoom?.id === room.id}
                onClick={() => setSelectedRoom(room)}
              >
                <ListItemText
                  primary={`Трек #${room.track}`}
                  secondary={room.last_message?.message?.slice(0, 50) || 'Нет сообщений'}
                />
              </ListItem>
            ))}
            {rooms.length === 0 && (
              <ListItem>
                <ListItemText primary="У вас пока нет активных чатов" />
              </ListItem>
            )}
          </List>
        </Paper>

        {/* Окно выбранного чата */}
        <div className="md:col-span-2 h-[600px]">
          {selectedRoom ? (
            <ChatRoom roomId={selectedRoom.id} currentUser={user} />
          ) : (
            <Paper className="h-full flex items-center justify-center">
              <Typography color="textSecondary">
                Выберите чат из списка
              </Typography>
            </Paper>
          )}
        </div>
      </div>
    </Container>
  );
};