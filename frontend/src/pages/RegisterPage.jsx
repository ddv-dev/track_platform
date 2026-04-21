import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Paper, TextField, Button, Typography, Box } from '@mui/material';
import { useAuth } from '../hooks/useAuth';

export const RegisterPage = () => {
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '', first_name: '', last_name: '' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const ok = await register(form);
    setLoading(false);
    if (ok) navigate('/login');
  };

  return (
    <Container maxWidth="sm" className="mt-20">
      <Paper elevation={3} className="p-8">
        <Typography variant="h4" component="h1" textAlign="center" gutterBottom>Регистрация</Typography>
        <form onSubmit={handleSubmit}>
          <TextField fullWidth label="Имя пользователя" margin="normal" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} required />
          <TextField fullWidth label="Email" type="email" margin="normal" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required />
          <TextField fullWidth label="Имя" margin="normal" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})} />
          <TextField fullWidth label="Фамилия" margin="normal" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})} />
          <TextField fullWidth label="Пароль" type="password" margin="normal" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required />
          <TextField fullWidth label="Подтверждение пароля" type="password" margin="normal" value={form.password2} onChange={(e) => setForm({...form, password2: e.target.value})} required />
          <Button fullWidth type="submit" variant="contained" size="large" disabled={loading} className="mt-4 btn-primary">{loading ? 'Регистрация...' : 'Зарегистрироваться'}</Button>
        </form>
        <Box className="mt-4 text-center"><Typography variant="body2">Уже есть аккаунт? <Link to="/login">Войдите</Link></Typography></Box>
      </Paper>
    </Container>
  );
};