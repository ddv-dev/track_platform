import api from './api';

export const chatService = {
  async getRooms() {
    const response = await api.get('/chat/rooms/');
    return response.data;
  },
  async createRoom(trackId) {
    const response = await api.post('/chat/rooms/create/', { track: trackId });
    return response.data;
  },
  async getRoom(roomId) {
    const response = await api.get(`/chat/rooms/${roomId}/`);
    return response.data;
  },
  async sendMessage(roomId, message) {
    const response = await api.post(`/chat/rooms/${roomId}/messages/`, { message });
    return response.data;
  },
  async markMessagesAsRead(roomId) {
    const response = await api.post(`/chat/rooms/${roomId}/mark-read/`);
    return response.data;
  },
  async createPrivateRoom(userId) {
    const response = await api.post('/chat/private/create/', { user_id: userId });
    return response.data;
  }
};