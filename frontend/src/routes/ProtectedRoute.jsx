import { useAuth } from '../context/AuthContext';
import { Outlet, Navigate } from 'react-router-dom';

const ProtectedRoute = () => {
    /*
    Handles user navigation via authentication
    If authenticated, allows access to route
    If not, navigates back to login page
    */
    const { loading, isAuthenticated } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;