import api from './request'

export const clientsApi = {
  getList: () => api.get('/clients/'),
  create: (data) => api.post('/clients/', data),
  getById: (id) => api.get(`/clients/${id}`),
  // 后端暂未实现修改和删除接口，如果后续后端加上了直接调用即可
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
}