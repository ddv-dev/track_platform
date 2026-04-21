import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Paper, TextField, Button, Typography, Box } from '@mui/material';
import { useAuth } from '../hooks/useAuth';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const ok = await login(username, password);
    setLoading(false);
    if (ok) navigate('/');
  };

  return (
    <Container maxWidth="sm" className="mt-20">
      <Paper elevation={3} className="p-8">
        <Typography variant="h4" component="h1" textAlign="center" gutterBottom>Вход в систему</Typography>
        <form onSubmit={handleSubmit}>
          <TextField fullWidth label="Имя пользователя" margin="normal" value={username} onChange={(e) => setUsername(e.target.value)} required />
          <TextField fullWidth label="Пароль" type="password" margin="normal" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button fullWidth type="submit" variant="contained" size="large" disabled={loading} className="mt-4 btn-primary">{loading ? 'Вход...' : 'Войти'}</Button>
        </form>
        <Box className="mt-4 text-center"><Typography variant="body2">Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link></Typography></Box>
      </Paper>
    </Container>
  );
};