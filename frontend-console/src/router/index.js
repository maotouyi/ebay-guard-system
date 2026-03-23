import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TaskManager from '../views/TaskManager.vue'
import ClientManager from '../views/ClientManager.vue'  // 新增

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Dashboard', component: Dashboard },
    { path: '/tasks', name: 'Tasks', component: TaskManager },
    { path: '/clients', name: 'Clients', component: ClientManager },
  ]
})

export default router