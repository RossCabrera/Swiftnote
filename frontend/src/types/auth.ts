// ============================================================================
// DOMAIN MODELS (Core entities)
// ============================================================================

export interface AuthUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    avatar: string | null;
    date_of_birth: string | null;
    age: number | null;
    is_verified: boolean;
}

// ============================================================================
// REQUEST PAYLOADS (What we send to the backend)
// ============================================================================

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    password_confirm: string;
    date_of_birth: string; 
    first_name: string;
    last_name: string;
}

export interface VerifyEmailRequest {
    token: string; // Token in url sent from email
}

export interface ResendVerificationRequest {
    email: string; 
}

export interface PasswordResetRequest {
    email: string; // Token in url sent from email
}

export interface PasswordResetVerifyRequest {
    token: string; 
}

export interface PasswordResetConfirmRequest {
    token: string;
    new_password: string;
    confirm_password: string;
}

export interface GoogleAuthRequest {
    access_token: string; // The token you get back from Google
}

// ============================================================================
// RESPONSE PAYLOADS (What the backend returns)
// ============================================================================

export interface AuthTokens {
    access: string;
}

export interface LoginResponse {
    access: string;
    user: AuthUser;
}

// Generic response for things like password reset or resend verification
export interface GenericSuccessResponse {
    detail: string;
}

// ============================================================================
// ZUSTAND STORE STATE (Frontend global state)
// ============================================================================

export interface AuthState {
    user: AuthUser | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    setAuth: (user: AuthUser, accessToken: string) => void;
    clearAuth: () => void;
    setLoading: (loading: boolean) => void;
}
