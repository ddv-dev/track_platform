import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper, List, ListItem, ListItemText, Button, CircularProgress, Box } from '@mui/material';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

export const CuratorRequestsPage = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === 'curator') loadRequests();
  }, [user]);

  const loadRequests = async () => {
    try {
      const res = await api.get('/tracks/curator/enrollment-requests/');
      setRequests(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (id, action) => {
    try {
      await api.post(`/tracks/curator/enrollment-requests/${id}/review/`, { action });
      toast.success(`Заявка ${action === 'accept' ? 'принята' : 'отклонена'}`);
      loadRequests(); // обновить список
    } catch (err) {
      toast.error('Ошибка');
    }
  };

  if (loading) return <div className="flex justify-center mt-8"><CircularProgress /></div>;

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6">Заявки на зачисление</Typography>
      <Paper>
        <List>
          {requests.length === 0 && <ListItem><ListItemText primary="Нет активных заявок" /></ListItem>}
          {requests.map(req => (
            <ListItem key={req.id} divider>
              <ListItemText
                primary={req.student_name}
                secondary={`Трек: ${req.track_name} | ${req.created_at}`}
              />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button variant="contained" color="success" onClick={() => handleReview(req.id, 'accept')}>Принять</Button>
                <Button variant="contained" color="error" onClick={() => handleReview(req.id, 'reject')}>Отклонить</Button>
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
};