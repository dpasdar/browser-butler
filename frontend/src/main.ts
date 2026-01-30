import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './pages/Dashboard.vue'
import TaskConfig from './pages/TaskConfig.vue'
import Logs from './pages/Logs.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/tasks/new', name: 'task-create', component: TaskConfig },
    { path: '/tasks/:id/edit', name: 'task-edit', component: TaskConfig },
    { path: '/logs', name: 'logs', component: Logs },
    { path: '/logs/:taskId', name: 'task-logs', component: Logs },
  ],
})

const app = createApp(App)
app.use(router)
app.mount('#app')
