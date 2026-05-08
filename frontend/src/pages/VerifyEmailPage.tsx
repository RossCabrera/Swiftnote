import { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { LoadingSpinner } from '../components/shared/LoadingSpinner';

export const VerifyEmailPage = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('');
    const hasAttempted = useRef(false);

    useEffect(() => {
        if (!token) {
            setStatus('error');
            setMessage('Invalid or missing verification token.');
            return;
        }

        // Prevent double firing in React Strict Mode
        if (hasAttempted.current) return;
        hasAttempted.current = true;

        const verify = async () => {
            try {
                await authService.verifyEmail({ token });
                setStatus('success');
                setMessage('Your email has been successfully verified! You can now log in.');
            } catch (err: any) {
                setStatus('error');
                setMessage(err.response?.data?.error || 'Verification failed. The link may have expired or already been used.');
            }
        };

        verify();
    }, [token]);

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
            <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100 text-center">
                {status === 'loading' && (
                    <div className="flex flex-col items-center gap-4">
                        <LoadingSpinner />
                        <h2 className="text-xl font-semibold text-gray-700">Verifying your email...</h2>
                    </div>
                )}

                {status === 'success' && (
                    <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
                            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Email Verified!</h2>
                        <p className="text-gray-600 mb-8">{message}</p>
                        <Link 
                            to="/login" 
                            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                        >
                            Go to Login
                        </Link>
                    </div>
                )}

                {status === 'error' && (
                    <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
                        <p className="text-gray-600 mb-8">{message}</p>
                        <div className="flex gap-4 w-full">
                            <Link 
                                to="/login" 
                                className="flex-1 py-2.5 px-4 border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition-colors"
                            >
                                Back to Login
                            </Link>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
