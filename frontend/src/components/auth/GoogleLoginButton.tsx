import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export const GoogleLoginButton = () => {
    const { googleAuth } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);

    const login = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            try {
                setError(null);
                // Send the access_token to the backend
                await googleAuth({ access_token: tokenResponse.access_token });
                navigate('/');
            } catch (err) {
                setError('Failed to log in with Google. Please try again.');
            }
        },
        onError: () => {
            setError('Google sign-in popup failed or was closed.');
        }
    });

    return (
        <div className="w-full flex flex-col items-center">
            <button
                type="button"
                onClick={() => login()}
                className="w-full flex justify-center items-center gap-3 py-2.5 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-semibold text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
            >
                <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-5 h-5" />
                Continue with Google
            </button>
            {error && <span className="text-sm font-medium text-red-500 mt-2">{error}</span>}
        </div>
    );
};
