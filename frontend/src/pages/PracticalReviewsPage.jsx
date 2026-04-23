import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper, List, ListItem, ListItemText, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Chip, CircularProgress } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import api from '../services/api';
export const PracticalReviewsPage = () => {
  const { user } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    if (user?.role === 'curator') {
      loadSubmissions();
    }
  }, [user]);

  const loadSubmissions = async () => {
    try {
      const response = await api.get('/tracks/curator/pending/');
      setSubmissions(response.data);
    } catch (error) {
      console.error(error);
      toast.error('Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = (submission, action) => {
    setSelectedSubmission(submission);
    setFeedback('');
    setOpenDialog(true);
  };

  const submitReview = async () => {
    if (!selectedSubmission) return;
    try {
      await api.post(`/tracks/curator/review/${selectedSubmission.id}/`, {
        action: 'approve', // или 'reject'
        feedback: feedback,
      });
      toast.success('Задание проверено');
      setOpenDialog(false);
      loadSubmissions(); // обновить список
    } catch (error) {
      toast.error('Ошибка при проверке');
    }
  };

  if (user?.role !== 'curator') {
    return <Container className="mt-8"><Typography>Доступ только для кураторов</Typography></Container>;
  }

  if (loading) return <div className="flex justify-center mt-8"><CircularProgress /></div>;

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6">Проверка практических заданий</Typography>
      <Paper>
        <List>
          {submissions.length === 0 && <ListItem><ListItemText primary="Нет заданий на проверку" /></ListItem>}
          {submissions.map(sub => (
            <ListItem key={sub.id} divider>
              <ListItemText
                primary={`${sub.task_title} – ${sub.user_name}`}
                secondary={sub.answer?.substring(0, 100) + (sub.answer?.length > 100 ? '…' : '')}
              />
              <div>
                <Button variant="outlined" color="success" onClick={() => handleReview(sub, 'approve')} sx={{ mr: 1 }}>Принять</Button>
                <Button variant="outlined" color="error" onClick={() => handleReview(sub, 'reject')}>Отклонить</Button>
              </div>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Проверка задания</DialogTitle>
        <DialogContent>
          <Typography variant="body2" className="mb-2"><strong>Ответ студента:</strong></Typography>
          <Paper variant="outlined" className="p-3 mb-4 bg-gray-50">{selectedSubmission?.answer}</Paper>
          <TextField
            label="Комментарий (опционально)"
            multiline
            rows={3}
            fullWidth
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
          <Button onClick={submitReview} variant="contained" color="primary">Подтвердить</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};