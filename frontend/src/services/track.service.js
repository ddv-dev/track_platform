import api from './api';

export const trackService = {
  async getDirections() {
    const response = await api.get('/tracks/directions/');
    return response.data;
  },
  async getTracks(params) {
    const response = await api.get('/tracks/', { params });
    return response.data;
  },
  async getTrack(id) {
    const response = await api.get(`/tracks/${id}/`);
    return response.data;
  },
  async submitTask(trackId, taskId, answer) {
    const response = await api.post(`/tracks/${trackId}/tasks/${taskId}/submit/`, { answer });
    return response.data;
  },
  async toggleChecklistItem(trackId, itemId) {
    const response = await api.post(`/tracks/${trackId}/checklist/${itemId}/toggle/`);
    return response.data;
  },
  async getTrackProgress(trackId) {
    const response = await api.get(`/tracks/${trackId}/progress/`);
    return response.data;
  },
  async getUserProgress() {
    const response = await api.get('/auth/progress/');
    return response.data;
  },
};