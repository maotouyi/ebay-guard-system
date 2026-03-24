import { createApp } from 'vue'
import './style.css' // 这句是让样式生效的灵魂
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')