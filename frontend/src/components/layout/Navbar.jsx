import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Avatar, Menu, MenuItem, Box, Container } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  return (
    <nav className="bg-gradient-to-r from-darkBlue to-blue sticky top-0 z-50 shadow-lg">
      <Container maxWidth="xl">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="flex items-center gap-2">
            <SchoolIcon sx={{ color: '#37EBFF', fontSize: 32 }} />
            <span className="text-white text-xl font-bold">
              МИСИС<span className="text-cyan">IT</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link to="/tracks" className="text-white hover:text-cyan transition">Треки</Link>
                <Link to="/chat" className="text-white hover:text-cyan transition">Чаты</Link>
                {/* Ссылки для куратора */}
                {user?.role === 'curator' && (
                  <>
                    <Link to="/curator/requests" className="text-white hover:text-cyan transition">Заявки</Link>
                    <Link to="/curator/stats" className="text-white hover:text-cyan transition">Статистика</Link>
                    <Link to="/curator/reviews" className="text-white hover:text-cyan transition">Проверка</Link>
                  </>
                )}
                {user?.role === 'teacher' && (
                  <>
                    <Link to="/teacher/tasks" className="text-white hover:text-cyan transition">Редактор заданий</Link>
                    <Link to="/teacher/stats" className="text-white hover:text-cyan transition">Результаты студентов</Link>
                  </>
                )}
                <Avatar
                  src={user?.avatar || undefined}
                  onClick={(e) => setAnchorEl(e.currentTarget)}
                  sx={{ bgcolor: '#37EBFF', color: '#0A1E64', cursor: 'pointer', width: 40, height: 40 }}
                >
                  {user?.first_name?.[0] || user?.username?.[0]}
                </Avatar>
                {anchorEl && (
                  <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
                    <MenuItem onClick={() => { navigate('/profile'); setAnchorEl(null); }}>Профиль</MenuItem>
                    <MenuItem onClick={logout}>Выйти</MenuItem>
                  </Menu>
                )}
              </>
            ) : (
              <div className="flex gap-3">
                <Link to="/login" className="px-5 py-2 rounded-xl border-2 border-cyan text-cyan hover:bg-cyan hover:text-darkBlue transition">
                  Вход
                </Link>
                <Link to="/register" className="px-5 py-2 rounded-xl bg-gradient-primary text-white hover:shadow-lg transition">
                  Регистрация
                </Link>
              </div>
            )}
          </div>
        </div>
      </Container>
    </nav>
  );
};