// src/api/request.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 10000,
});

api.interceptors.request.use(
    (config) => config,
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error("API 请求爆炸了:", error);
        return Promise.reject(error);
    }
);

// 👇 就是这句！决定了外面能不能拿到这个 api 对象
export default api;