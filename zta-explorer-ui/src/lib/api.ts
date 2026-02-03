import axios from 'axios';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

const normaliseBaseUrl = (url: string) => url.replace(/\/$/, '');

export const API_BASE_URL = normaliseBaseUrl(import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL);

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.data?.detail) {
            error.message = error.response.data.detail;
        }
        return Promise.reject(error);
    }
);
