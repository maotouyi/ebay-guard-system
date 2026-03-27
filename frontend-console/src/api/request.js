import axios from 'axios'
import { useToast } from '../utils/toast'

const { error: showError } = useToast()

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
    timeout: 15000,
})

api.interceptors.request.use(
    (config) => config,
    (error) => Promise.reject(error)
)

api.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error("API 请求爆炸了:", error)
        const errorMsg = error.response?.data?.detail || error.message || '网络请求失败'
        showError(errorMsg)
        return Promise.reject(error)
    }
)

export default api