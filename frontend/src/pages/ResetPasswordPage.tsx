import { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { FormField } from '../components/shared/FormField';
import { LoadingSpinner } from '../components/shared/LoadingSpinner';

export const ResetPasswordPage = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();

    const [status, setStatus] = useState<'verifying' | 'idle' | 'loading' | 'success' | 'invalid'>('verifying');
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({ password: '', password_confirm: '' });

    // Validate the token as soon as the page loads
    useEffect(() => {
        if (!token) {
            setStatus('invalid');
            setError('Missing reset token in URL.');
            return;
        }

        const verifyToken = async () => {
            try {
                await authService.passwordResetVerify({ token });
                setStatus('idle');
            } catch (err: any) {
                setStatus('invalid');
                setError(err.response?.data?.error || 'Invalid or expired reset link.');
            }
        };

        verifyToken();
    }, [token]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (formData.password !== formData.password_confirm) {
            return setError('Passwords do not match.');
        }

        setStatus('loading');
        setError('');
        
        try {
            await authService.passwordResetConfirm({
                token: token!,
                new_password: formData.password,
                confirm_password: formData.password_confirm
            });
            setStatus('success');
            // Give them a few seconds to see the success message before redirecting
            setTimeout(() => navigate('/login'), 3500);
        } catch (err: any) {
            setStatus('idle');
            const errorData = err.response?.data;
            if (errorData && typeof errorData === 'object' && !errorData.error) {
                const firstErrorKey = Object.keys(errorData)[0];
                setError(`${firstErrorKey}: ${errorData[firstErrorKey]}`);
            } else {
                setError(errorData?.error || 'Failed to reset password.');
            }
        }
    };

    if (status === 'verifying') {
        return <LoadingSpinner fullScreen />;
    }

    if (status === 'invalid') {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
                <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100 text-center animate-in fade-in zoom-in duration-300">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Invalid Link</h2>
                    <p className="text-red-600 mb-6">{error}</p>
                    <Link to="/forgot-password" className="text-blue-600 font-medium hover:text-blue-500">Request a new link</Link>
                </div>
            </div>
        );
    }

    if (status === 'success') {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
                <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100 text-center animate-in fade-in zoom-in duration-300">
                    <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-6">
                        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Password Reset!</h2>
                    <p className="text-gray-600">Your password has been successfully reset. Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen bg-gray-50 py-12 px-4">
            <div className="m-auto w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">New Password</h1>
                    <p className="text-gray-500">Enter your new secure password</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-100">
                            {error}
                        </div>
                    )}
                    
                    <FormField 
                        label="New Password" 
                        type="password" 
                        id="password" 
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        required 
                        minLength={8}
                    />
                    <FormField 
                        label="Confirm Password" 
                        type="password" 
                        id="password_confirm" 
                        placeholder="••••••••"
                        value={formData.password_confirm}
                        onChange={(e) => setFormData({...formData, password_confirm: e.target.value})}
                        required 
                    />

                    <button
                        type="submit"
                        disabled={status === 'loading'}
                        className="w-full mt-4 flex justify-center py-2.5 px-4 rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-70 transition-all"
                    >
                        {status === 'loading' ? 'Resetting...' : 'Reset Password'}
                    </button>
                </form>
            </div>
        </div>
    );
};
