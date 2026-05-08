import { create } from 'zustand';
import type { AuthState } from '../types/auth';

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: true,  

    // Actions
    setAuth: (user, accessToken) =>
        set({ 
            user, 
            accessToken, 
            isAuthenticated: true, 
            isLoading: false 
        }),

    clearAuth: () =>
        set({ 
            user: null, 
            accessToken: null, 
            isAuthenticated: false, 
            isLoading: false 
        }),

    setLoading: (isLoading) => set({ isLoading }),
}));
