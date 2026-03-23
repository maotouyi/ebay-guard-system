import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TaskManager from '../views/TaskManager.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Dashboard', component: Dashboard },
    { path: '/tasks', name: 'Tasks', component: TaskManager }, // 新增这行
  ]
})

export default router