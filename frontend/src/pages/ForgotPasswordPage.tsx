import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { FormField } from '../components/shared/FormField';

export const ForgotPasswordPage = () => {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('loading');
        
        try {
            await authService.passwordResetRequest({ email });
            setStatus('success');
            setMessage('If an account exists with this email, you will receive a password reset link shortly.');
        } catch (err: any) {
            setStatus('error');
            setMessage(err.response?.data?.error || 'Failed to request password reset. Please try again.');
        }
    };

    return (
        <div className="flex min-h-screen bg-gray-50 py-12 px-4">
            <div className="m-auto w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">Reset Password</h1>
                    <p className="text-gray-500">Enter your email and we'll send you a link</p>
                </div>

                {status === 'success' ? (
                    <div className="text-center animate-in fade-in duration-300">
                        <div className="bg-green-50 text-green-700 p-4 rounded-lg mb-6 border border-green-100">
                            {message}
                        </div>
                        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                            Return to Login
                        </Link>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {status === 'error' && (
                            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-100">
                                {message}
                            </div>
                        )}
                        
                        <FormField 
                            label="Email Address" 
                            type="email" 
                            id="email" 
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required 
                        />

                        <button
                            type="submit"
                            disabled={status === 'loading'}
                            className="w-full flex justify-center py-2.5 px-4 rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 transition-all"
                        >
                            {status === 'loading' ? 'Sending...' : 'Send Reset Link'}
                        </button>
                        
                        <div className="text-center mt-4">
                            <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                                Back to Login
                            </Link>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};
