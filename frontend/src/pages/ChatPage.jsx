// frontend/src/pages/ChatPage.jsx
import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper, List, ListItem, ListItemText, CircularProgress, Tabs, Tab, Box } from '@mui/material';
import { chatService } from '../services/chat.service';
import { ChatRoom } from '../components/chat/ChatRoom';
import { UserSearch } from '../components/chat/UserSearch';
import { useAuth } from '../hooks/useAuth';
import GroupIcon from '@mui/icons-material/Group';
import PersonIcon from '@mui/icons-material/Person';

export const ChatPage = () => {
  const { user } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0); // 0 - групповые, 1 - личные

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      const data = await chatService.getRooms();
      let roomsArray = [];
      if (Array.isArray(data)) roomsArray = data;
      else if (data?.results && Array.isArray(data.results)) roomsArray = data.results;
      else if (data && typeof data === 'object') roomsArray = [data];
      setRooms(roomsArray);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const groupRooms = rooms.filter(room => room.is_group_chat === true);
  const privateRooms = rooms.filter(room => !room.is_group_chat);

  const handleChatCreated = () => {
    loadRooms(); // обновить список чатов после создания нового
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
        Чаты
      </Typography>

      {/* Поиск пользователей для создания новых чатов */}
      <UserSearch currentUser={user} onChatCreated={handleChatCreated} />

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} className="mb-4">
        <Tab label="Групповые чаты" icon={<GroupIcon />} iconPosition="start" />
        <Tab label="Личные чаты" icon={<PersonIcon />} iconPosition="start" />
      </Tabs>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Список чатов */}
        <Paper className="h-[600px] overflow-y-auto">
          {tabValue === 0 && (
            <List>
              {groupRooms.length === 0 ? (
                <ListItem>
                  <ListItemText primary="Нет групповых чатов" />
                </ListItem>
              ) : (
                groupRooms.map((room) => (
                  <ListItem
                    button
                    key={room.id}
                    selected={selectedRoom?.id === room.id}
                    onClick={() => setSelectedRoom(room)}
                  >
                    <ListItemText
                      primary={room.title || `Группа трека #${room.track}`}
                      secondary={room.last_message?.message?.slice(0, 50) || 'Нет сообщений'}
                    />
                  </ListItem>
                ))
              )}
            </List>
          )}
          {tabValue === 1 && (
            <List>
              {privateRooms.length === 0 ? (
                <ListItem>
                  <ListItemText primary="Нет личных чатов" />
                </ListItem>
              ) : (
                privateRooms.map((room) => {
                  const otherUser = room.student?.id === user?.id ? room.curator : room.student;
                  return (
                    <ListItem
                      button
                      key={room.id}
                      selected={selectedRoom?.id === room.id}
                      onClick={() => setSelectedRoom(room)}
                    >
                      <ListItemText
                        primary={otherUser ? `${otherUser.first_name} ${otherUser.last_name}` : 'Пользователь'}
                        secondary={room.last_message?.message?.slice(0, 50) || 'Нет сообщений'}
                      />
                    </ListItem>
                  );
                })
              )}
            </List>
          )}
        </Paper>

        {/* Окно чата */}
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