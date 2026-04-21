import { useAuthStore } from '../store/authStore';
import { authService } from '../services/auth.service';
import toast from 'react-hot-toast';

export const useAuth = () => {
  const { user, isAuthenticated, setUser, logout } = useAuthStore();

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);
      setUser(response.user);
      toast.success('Добро пожаловать!');
      return true;
    } catch {
      toast.error('Неверное имя пользователя или пароль');
      return false;
    }
  };

  const register = async (data) => {
    try {
      await authService.register(data);
      toast.success('Регистрация успешна! Теперь войдите.');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.password?.[0] || 'Ошибка регистрации');
      return false;
    }
  };

  const handleLogout = () => {
    authService.logout();
    logout();
    toast.success('Вы вышли из системы');
  };

  return { user, isAuthenticated, login, register, logout: handleLogout };
};