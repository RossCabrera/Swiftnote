import { useAuth } from '../hooks/useAuth';

export const DashboardPage = () => {
    const { user, logout } = useAuth();
    
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Protected Dashboard</h1>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-lg mb-4">
                    Welcome to the secret area, <strong>{user?.email || 'User'}</strong>!
                </p>
                
                <button 
                    onClick={logout}
                    className="bg-red-500 hover:bg-red-600 text-white font-medium px-4 py-2 rounded transition-colors"
                >
                    Log Out
                </button>
            </div>
        </div>
    );
};
