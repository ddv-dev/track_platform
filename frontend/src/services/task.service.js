import api from './api';

export const taskService = {
  async getTrackTasks(trackId) {
    const response = await api.get(`/tracks/${trackId}/tasks/`);
    return response.data;
  },
  async submitTask(taskId, answer) {
    const response = await api.post(`/tracks/tasks/${taskId}/submit/`, { answer });
    return response.data;
  },

  async updateTask(trackId, taskId, taskData) {
    const response = await api.put(`/tracks/${trackId}/tasks/${taskId}/`, taskData);
    return response.data;
  },

  async createTask(trackId, taskData) {
    const response = await api.post(`/tracks/${trackId}/tasks/`, taskData);
    return response.data;
  }
};