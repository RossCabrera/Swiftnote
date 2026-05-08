import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FormField } from '../components/shared/FormField';
import { GoogleLoginButton } from '../components/auth/GoogleLoginButton';

export const RegisterPage = () => {
    const { register, isLoading } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({ 
        first_name: '', 
        last_name: '', 
        email: '', 
        date_of_birth: '',
        password: '', 
        password_confirm: '' 
    });
    
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (formData.password !== formData.password_confirm) {
            return setError("Passwords do not match");
        }

        try {
            await register(formData);
            // Redirect to login page with success message
            navigate('/login', { 
                state: { message: "Account created! Please check your email to verify your account before logging in." }
            });
        } catch (err: any) {
            // Display backend validation errors
            const errorData = err.response?.data;
            if (errorData && typeof errorData === 'object' && !errorData.detail) {
                const firstErrorKey = Object.keys(errorData)[0];
                setError(`${firstErrorKey}: ${errorData[firstErrorKey]}`);
            } else {
                setError(err.response?.data?.detail || 'Registration failed. Please try again.');
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    return (
        <div className="flex min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="m-auto w-full max-w-lg bg-white p-8 sm:p-10 rounded-2xl shadow-xl border border-gray-100">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">Create an Account</h1>
                    <p className="text-gray-500">Start capturing your thoughts today</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 border border-red-100">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <FormField 
                            label="First Name" 
                            id="first_name" 
                            placeholder="Jane"
                            value={formData.first_name}
                            onChange={handleChange}
                            required 
                        />
                        <FormField 
                            label="Last Name" 
                            id="last_name" 
                            placeholder="Doe"
                            value={formData.last_name}
                            onChange={handleChange}
                            required 
                        />
                    </div>

                    <FormField 
                        label="Email Address" 
                        type="email" 
                        id="email" 
                        placeholder="you@example.com"
                        value={formData.email}
                        onChange={handleChange}
                        required 
                    />

                    <FormField 
                        label="Date of Birth" 
                        type="date" 
                        id="date_of_birth" 
                        value={formData.date_of_birth}
                        onChange={handleChange}
                        required 
                    />
                    
                    <FormField 
                        label="Password" 
                        type="password" 
                        id="password" 
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={handleChange}
                        required 
                        minLength={8}
                    />

                    <FormField 
                        label="Confirm Password" 
                        type="password" 
                        id="password_confirm" 
                        placeholder="••••••••"
                        value={formData.password_confirm}
                        onChange={handleChange}
                        required 
                    />

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full mt-4 flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all"
                    >
                        {isLoading ? (
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : 'Create Account'}
                    </button>
                </form>

                <div className="mt-7">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-3 bg-white text-gray-500 font-medium">Or register with</span>
                        </div>
                    </div>

                    <div className="mt-6 flex justify-center">
                        <GoogleLoginButton />
                    </div>
                </div>

                <p className="mt-8 text-center text-sm text-gray-600">
                    Already have an account?{' '}
                    <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
                        Sign in instead
                    </Link>
                </p>
            </div>
        </div>
    );
};
