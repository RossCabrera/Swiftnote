import axios from 'axios';
import api from '../lib/axios';
import type { 
    AuthUser,
    LoginRequest, 
    LoginResponse,
    RegisterRequest, 
    VerifyEmailRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetVerifyRequest,
    PasswordResetConfirmRequest,
    GoogleAuthRequest,
    GenericSuccessResponse
} from '../types/auth';

export const authService = {
    
    // ========================================================================
    // LOGIN & OAUTH
    // ========================================================================
    
    login: (data: LoginRequest) => {
        return api.post<LoginResponse>('/api/auth/login/', data);
    },
    
    googleAuth: (data: GoogleAuthRequest) => {
        return api.post<LoginResponse>('/api/auth/google/', data);
    },

    logout: () => {
        return api.post<GenericSuccessResponse>('/api/auth/logout/');
    },


    refresh: () => {
        const BASE_URL = import.meta.env.VITE_API_BASE_URL;
        return axios.post<{ access: string }>(`${BASE_URL}/api/auth/refresh/`, {}, {
            withCredentials: true
        });
    },

    getCurrentUser: () => {
        return api.get<AuthUser>('/api/auth/current-user/');
    },

    // ========================================================================
    // REGISTRATION & VERIFICATION
    // ========================================================================
    
    register: (data: RegisterRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/register/', data);
    },

    verifyEmail: (data: VerifyEmailRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/verify-email/', data);
    },

    resendVerification: (data: ResendVerificationRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/resend-verification/', data);
    },

    // ========================================================================
    // PASSWORD RESET FLOW
    // ========================================================================
    
    passwordResetRequest: (data: PasswordResetRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/password-reset/', data);
    },

    passwordResetVerify: (data: PasswordResetVerifyRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/password-reset/verify/', data);
    },

    passwordResetConfirm: (data: PasswordResetConfirmRequest) => {
        return api.post<GenericSuccessResponse>('/api/auth/password-reset/confirm/', data);
    }
};
