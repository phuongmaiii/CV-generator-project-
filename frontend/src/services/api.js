import axios from 'axios';

const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL = RAW_BASE_URL
    ? `${RAW_BASE_URL.replace(/\/$/, '')}/api`
    : 'https://cv-generator-project.onrender.com/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 0, 
});

api.interceptors.request.use((config) => {
    // Tìm token trực tiếp hoặc nằm bên trong object user
    const directToken = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    let finalToken = directToken;

    if (!finalToken && userStr) {
        try {
            const user = JSON.parse(userStr);
            finalToken = user.token;
        } catch (e) {}
    }

    if (finalToken) {
        config.headers.Authorization = `Bearer ${finalToken}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;