import React, { useState } from 'react';
import { TextField, List, ListItem, ListItemText, Button, Paper } from '@mui/material';
import api from '../../services/api';
import { chatService } from '../../services/chat.service';
import toast from 'react-hot-toast';

export const UserSearch = ({ currentUser, onChatCreated }) => {
    const [query, setQuery] = useState('');
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const role = currentUser.role === 'student' ? 'teacher' : 'student';
            const response = await api.get(`/chat/users/search/?q=${query}&role=${role}`);
            setUsers(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const startChat = async (userId) => {
        try {
            await chatService.createPrivateRoom(userId);
            toast.success('Чат создан!');
            onChatCreated(); // обновить список чатов
        } catch (error) {
            toast.error('Не удалось создать чат');
        }
    };

    return (
        <Paper className="p-4 mb-4">
            <div className="flex gap-2">
                <TextField
                    fullWidth
                    label="Поиск пользователей"
                    variant="outlined"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button variant="contained" onClick={handleSearch}>Найти</Button>
            </div>
            <List>
                {users.map(user => (
                    <ListItem key={user.id} divider>
                        <ListItemText primary={`${user.first_name} ${user.last_name}`} secondary={user.username} />
                        <Button variant="outlined" onClick={() => startChat(user.id)}>Написать</Button>
                    </ListItem>
                ))}
            </List>
        </Paper>
    );
};