import api from './api';

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login/', { username, password });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
  },
  async register(data) {
    return api.post('/auth/register/', data);
  },
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  async getProfile() {
    const response = await api.get('/auth/profile/');
    return response.data;
  },
  async updateProfile(data) {
    const response = await api.patch('/auth/profile/', data);
    return response.data;
  },
};