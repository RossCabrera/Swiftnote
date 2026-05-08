import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/authService';
import { FormField } from '../components/shared/FormField';
import { GoogleLoginButton } from '../components/auth/GoogleLoginButton';

export const LoginPage = () => {
    const { login, isLoading } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    
    // Default redirect after successful login
    const from = location.state?.from?.pathname || '/';

    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState<string | null>(null);
    const [resendStatus, setResendStatus] = useState<'idle' | 'loading' | 'success'>('idle');
    const [resendMessage, setResendMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setResendStatus('idle');

        try {
            await login(formData);
            navigate(from, { replace: true });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to login. Please check your credentials.');
        }
    };

    const handleResend = async () => {
        if (!formData.email) return;
        setResendStatus('loading');
        try {
            await authService.resendVerification({ email: formData.email });
            setResendStatus('success');
            setResendMessage('Verification email sent! Please check your inbox.');
        } catch (err: any) {
            setResendStatus('idle');
            setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to resend email.');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    return (
        <div className="flex min-h-screen bg-gray-50">
            <div className="m-auto w-full max-w-md bg-white p-8 sm:p-10 rounded-2xl shadow-xl border border-gray-100">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">Welcome Back</h1>
                    <p className="text-gray-500">Sign in to continue to Swiftnote</p>
                </div>

                {/* Display Success Message from Registration  */}
                {location.state?.message && (
                    <div className="bg-green-50 text-green-700 p-3 rounded-lg text-sm mb-6 border border-green-100">
                        {location.state.message}
                    </div>
                )}

                {/* Display Errors */}
                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 border border-red-100 flex flex-col gap-2">
                        <span>{error}</span>
                        {error.toLowerCase().includes('not verified') && (
                            <button 
                                type="button" 
                                onClick={handleResend}
                                disabled={resendStatus === 'loading'}
                                className="text-left font-semibold text-blue-600 hover:text-blue-700 underline text-sm disabled:opacity-50"
                            >
                                {resendStatus === 'loading' ? 'Sending...' : 'Click here to resend verification email'}
                            </button>
                        )}
                    </div>
                )}
                
                {resendStatus === 'success' && (
                    <div className="bg-green-50 text-green-700 p-3 rounded-lg text-sm mb-6 border border-green-100">
                        {resendMessage}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <FormField 
                        label="Email Address" 
                        type="email" 
                        id="email" 
                        placeholder="you@example.com"
                        value={formData.email}
                        onChange={handleChange}
                        required 
                    />
                    
                    <div className="space-y-1">
                        <FormField 
                            label="Password" 
                            type="password" 
                            id="password" 
                            placeholder="••••••••"
                            value={formData.password}
                            onChange={handleChange}
                            required 
                        />
                        <div className="flex justify-end pt-1">
                            <Link to="/forgot-password" className="text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors">
                                Forgot password?
                            </Link>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full flex justify-center items-center py-2.5 px-4 mt-2 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all"
                    >
                        {isLoading ? (
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : 'Sign In'}
                    </button>
                </form>

                <div className="mt-7">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-3 bg-white text-gray-500 font-medium">Or continue with</span>
                        </div>
                    </div>

                    <div className="mt-6 flex justify-center">
                        <GoogleLoginButton />
                    </div>
                </div>

                <p className="mt-8 text-center text-sm text-gray-600">
                    Don't have an account?{' '}
                    <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
                        Sign up for free
                    </Link>
                </p>
            </div>
        </div>
    );
};
