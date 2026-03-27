import api from './request'

export const alertsApi = {
  getDashboardStats: () => api.get('/alerts/dashboard'),
  getAlertLogs: (limit = 50) => api.get(`/alerts/?limit=${limit}`),
}