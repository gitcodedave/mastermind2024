import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import LoginRegisterPage from '../pages/loginregistepage';
import GamePage from '../pages/gamepage';


export function AppRoutes() {
    return (
        <>
            <Routes>
                {/* Home page */}
                <Route exact path="/login" element={<LoginRegisterPage />} />

                {/* Protected Routes */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/game" element={<GamePage />} />
                </Route>

                {/* Catch all other urls */}
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
        </>
    );
}


export default AppRoutes;