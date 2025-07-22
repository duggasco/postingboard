import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export const ideaApi = {
  getIdeas: (params = {}) => api.get('/ideas', { params }),
  createIdea: (data) => api.post('/ideas', data),
  getIdea: (id) => api.get(`/ideas/${id}`),
  claimIdea: (id, data) => api.post(`/ideas/${id}/claim`, data),
  completeIdea: (id) => api.post(`/ideas/${id}/complete`),
};

export const skillApi = {
  getSkills: () => api.get('/skills'),
};

export const authApi = {
  login: (password) => api.post('/auth/login', { password }),
  logout: () => api.post('/auth/logout'),
  checkAuth: () => api.get('/auth/check'),
};

export const adminApi = {
  updateIdea: (id, data) => api.put(`/admin/ideas/${id}`, data),
  deleteIdea: (id) => api.delete(`/admin/ideas/${id}`),
  createSkill: (data) => api.post('/admin/skills', data),
  updateSkill: (id, data) => api.put(`/admin/skills/${id}`, data),
  deleteSkill: (id) => api.delete(`/admin/skills/${id}`),
};

export default api;