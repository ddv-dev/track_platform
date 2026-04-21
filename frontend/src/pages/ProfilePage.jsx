import React, { useEffect, useState } from 'react';
import { Container, Paper, Typography, Avatar, TextField, Button, CircularProgress } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth.service';
import { trackService } from '../services/track.service';
import toast from 'react-hot-toast';

export const ProfilePage = () => {
  const { user, setUser } = useAuth();
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', telegram: '' });

  useEffect(() => { if (user) { setForm({ first_name: user.first_name || '', last_name: user.last_name || '', email: user.email || '', phone: user.phone || '', telegram: user.telegram || '' }); loadProgress(); } }, [user]);

  const loadProgress = async () => {
    try { const data = await trackService.getUserProgress(); setProgress(data); } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  const handleUpdate = async () => {
    try {
      const updated = await authService.updateProfile(form);
      setUser(updated);
      toast.success('Профиль обновлён');
    } catch { toast.error('Ошибка обновления'); }
  };

  if (!user) return <Container className="mt-8"><Typography>Загрузка...</Typography></Container>;

  return (
    <Container className="py-8">
      <Paper className="p-6 mb-6">
        <div className="flex items-center gap-4 mb-6">
          <Avatar src={user.avatar || undefined} sx={{ width: 80, height: 80, bgcolor: '#37EBFF', color: '#0A1E64' }}>{user.first_name?.[0] || user.username[0]}</Avatar>
          <div><Typography variant="h5">{user.first_name} {user.last_name}</Typography><Typography color="textSecondary">@{user.username}</Typography></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TextField label="Имя" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})} fullWidth />
          <TextField label="Фамилия" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})} fullWidth />
          <TextField label="Email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} fullWidth />
          <TextField label="Телефон" value={form.phone} onChange={(e) => setForm({...form, phone: e.target.value})} fullWidth />
          <TextField label="Telegram" value={form.telegram} onChange={(e) => setForm({...form, telegram: e.target.value})} fullWidth />
        </div>
        <Button variant="contained" onClick={handleUpdate} className="mt-6 btn-primary">Сохранить изменения</Button>
      </Paper>
      <Paper className="p-6">
        <Typography variant="h6" className="mb-4">Мой прогресс</Typography>
        {loading ? <CircularProgress /> : progress.map((p) => (
          <div key={p.id} className="mb-3"><Typography>{p.track_name}</Typography><div className="progress-bar"><div className="progress-bar-fill" style={{ width: `${(p.completed_tasks_count / p.total_tasks_count) * 100}%` }} /></div><Typography variant="caption">{p.completed_tasks_count} / {p.total_tasks_count} заданий</Typography></div>
        ))}
      </Paper>
    </Container>
  );
};