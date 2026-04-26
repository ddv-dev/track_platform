import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Avatar, Menu, MenuItem, Container, Button } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/');
  };

  return (
    <nav className="bg-gradient-to-r from-darkBlue to-blue sticky top-0 z-50 shadow-lg">
      <Container maxWidth="xl">
        <div className="flex justify-between items-center py-4">
          {/* Логотип */}
          <Link to="/" className="flex items-center gap-2">
            <SchoolIcon sx={{ color: '#37EBFF', fontSize: 32 }} />
            <span className="text-white text-xl font-bold">
              МИСИС<span className="text-cyan">IT</span>
            </span>
          </Link>

          {/* Правая часть */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                {/* Общие для всех авторизованных */}
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

                {/* Ссылки для преподавателя */}
                {user?.role === 'teacher' && (
                  <>
                    <Link to="/teacher/tasks" className="text-white hover:text-cyan transition">Задания</Link>
                    <Link to="/teacher/stats" className="text-white hover:text-cyan transition">Результаты</Link>
                  </>
                )}

                {/* Аватар и меню */}
                <Avatar
                  src={user?.avatar || undefined}
                  onClick={handleMenuOpen}
                  sx={{ bgcolor: '#37EBFF', color: '#0A1E64', cursor: 'pointer', width: 40, height: 40 }}
                >
                  {user?.first_name?.[0] || user?.username?.[0]}
                </Avatar>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                  keepMounted
                >
                  <MenuItem onClick={() => { navigate('/profile'); handleMenuClose(); }}>Профиль</MenuItem>
                  <MenuItem onClick={handleLogout}>Выйти</MenuItem>
                </Menu>
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