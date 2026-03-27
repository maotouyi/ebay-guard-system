import api from './request'

export const tasksApi = {
  getList: () => api.get('/tasks/'),
  create: (data) => api.post('/tasks/', data),
  toggleActive: (id) => api.put(`/tasks/${id}/toggle`),
}