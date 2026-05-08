import axios from 'axios';
import { useAuthStore } from '../store/authStore';
import type { AuthTokens } from '../types/auth';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const TIMEOUT  = 30_000;  // 30 seconds

// ============================================================================
// AXIOS INSTANCE CONFIGURATION
// ============================================================================
export const api = axios.create({
    baseURL: BASE_URL,
    timeout: TIMEOUT,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
});

// ============================================================================
// REFRESH TOKEN QUEUE
// ============================================================================
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = [];

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token!);
        }
    });
    failedQueue = [];
};

// ============================================================================
// REQUEST INTERCEPTOR — Inject Access Token
// ============================================================================
api.interceptors.request.use((config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

// ============================================================================
// RESPONSE INTERCEPTOR — Handle 401 & Silent Token Refresh
// ============================================================================
const PUBLIC_AUTH_ENDPOINTS = [
    '/api/auth/login/',
    '/api/auth/refresh/',
    '/api/auth/register/',
    '/api/auth/google/',
];

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        const requestUrl: string = originalRequest?.url ?? '';

        const isPublicAuthEndpoint = PUBLIC_AUTH_ENDPOINTS.some(ep => requestUrl.includes(ep));

        if (error.response?.status === 401 && !originalRequest._retry && !isPublicAuthEndpoint) {
            
            // If already refreshing, queue this request and wait
            if (isRefreshing) {
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // The browser sends the httpOnly refresh cookie automatically.
                const response = await axios.post<AuthTokens>(
                    `${BASE_URL}/api/auth/refresh/`,
                    {},
                    { withCredentials: true }
                );

                const newAccessToken = response.data.access;

                // Update the in-memory access token in Zustand
                const { user, setAuth } = useAuthStore.getState();
                if (user) {
                    setAuth(user, newAccessToken);
                }

                processQueue(null, newAccessToken);

                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return api(originalRequest);

            } catch (refreshError) {
                // Refresh token is expired or invalid — force full logout
                processQueue(refreshError, null);
                useAuthStore.getState().clearAuth();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default api;
