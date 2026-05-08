import { useAuthStore } from '../store/authStore';
import { authService } from '../services/authService';
import type { 
    LoginRequest, 
    RegisterRequest, 
    GoogleAuthRequest 
} from '../types/auth';

export function useAuth() {
    const store = useAuthStore();

    // ------------------------------------------------------------------------
    // LOGIN
    // ------------------------------------------------------------------------
    const login = async (credentials: LoginRequest) => {
        store.setLoading(true);
        try {
            const { data } = await authService.login(credentials);
            store.setAuth(data.user, data.access);
            return data;
        } catch (error) {
            store.setLoading(false);
            throw error;
        }
    };

    // ------------------------------------------------------------------------
    // REGISTER
    // ------------------------------------------------------------------------
    const register = async (credentials: RegisterRequest) => {
        store.setLoading(true);
        try {
            const { data } = await authService.register(credentials);
            store.setLoading(false);
            return data;
        } catch (error) {
            store.setLoading(false);
            throw error;
        }
    };

    // ------------------------------------------------------------------------
    // GOOGLE OAUTH
    // ------------------------------------------------------------------------
    const googleAuth = async (credentials: GoogleAuthRequest) => {
        store.setLoading(true);
        try {
            const { data } = await authService.googleAuth(credentials);
            store.setAuth(data.user, data.access);
            return data;
        } catch (error) {
            store.setLoading(false);
            throw error;
        }
    };

    // ------------------------------------------------------------------------
    // LOGOUT
    // ------------------------------------------------------------------------
    const logout = async () => {
        store.setLoading(true);
        try {
            await authService.logout();
        } catch (error) {
            console.error("Server logout failed, clearing local state anyway.", error);
        } finally {
            store.clearAuth();
        }
    };

    // ------------------------------------------------------------------------
    // CHECK SESSION
    // ------------------------------------------------------------------------
    const checkSession = async () => {
        try {
            const { data: tokenData } = await authService.refresh();

            useAuthStore.getState().setAuth({ id: '', email: '', first_name: '', last_name: '', full_name: '', avatar: null, date_of_birth: null, age: null, is_verified: false }, tokenData.access);

            const { data: user } = await authService.getCurrentUser();

            store.setAuth(user, tokenData.access);

        } catch {
            store.setLoading(false);
        }
    };

    return {
        ...store,
        login,
        register,
        googleAuth,
        logout,
        checkSession
    };
}
