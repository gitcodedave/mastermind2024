import { createContext, useEffect, useState, useCallback, useContext } from 'react';
import { useCookies } from 'react-cookie';
import { jwtDecode } from 'jwt-decode';
import { API } from '../api/api';


const AuthContext = createContext();

export const AuthProvider = ({ children }) => {

    /*
    Creates context to be passed to the rest of the frontend framework
    register - accepts new credentials (username, password) creates new user
    getToken - accepts login credentials (username, password) to receive new tokens
    login - accepts the username, access token, refresh token - sets them as cookies
    logout - removes cookies: username, access token, and refresh token
    */
    const [cookies, setCookie, removeCookie] = useCookies(['AccessToken', 'Player', 'PreviousPlayer', 'PauseTime']);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);


    const register = async (credentials) => {
        try {
            const response = await API.post('/auth/users/', credentials);
            return response
        } catch (error) {
            console.log(error, 'Error trying to register')
            return error.response;
        }
    };


    const getToken = async (credentials) => {
        try {
            const response = await API.post('/auth/jwt/create', credentials);
            return response.data;
        } catch (error) {
            console.error('Error getting token:', error);
            return null;
        }
    };


    const isTokenValid = useCallback(async (token) => {
        /*
        Utility function
        Checks if token is valid and returns boolean value
        */
        const tokenObject = {
            "token": token
        }
        try {
            let isValid = await API.post('/auth/jwt/verify', tokenObject)
            if (isValid.data.code) {
                return false
            }
            return true
        } catch (error) {
            console.log(error, 'Unable to verify token')
            return false
        }
    }, []);


    const isTokenExpired = (token) => {
        /*
        Utility function
        Compares access token's expiration date with current date and returns boolean
        */
        if (!token) return true;
        const decodedToken = jwtDecode(token);
        const expiryTime = decodedToken.exp * 1000;
        return Date.now() > expiryTime;
    };


    const login = (playerName, accessToken, refreshToken) => {
        if (playerName !== cookies.PreviousPlayer) {
            removeCookie('PauseTime')
        }
        setCookie('Player', playerName, { path: '/' });
        setCookie('AccessToken', accessToken, { path: '/' });
        setCookie('RefreshToken', refreshToken, { path: '/' });
        setLoading(false);
        setIsAuthenticated(true);
    };


    const logout = useCallback((playerName) => {
        setCookie('PreviousPlayer', cookies.Player, { path: '/' });
        const currentPauseTime = new Date();
        setCookie('PauseTime', currentPauseTime.toISOString(), { path: '/' })
        removeCookie('Player', { path: '/' });
        removeCookie('AccessToken', { path: '/' });
        removeCookie('RefreshToken', { path: '/' });
        setIsAuthenticated(false)
    }, [removeCookie, setCookie, cookies.Player]);


    const refreshToken = useCallback(async () => {
        /*
        Returns new access token using refresh token, resets cookie
        */
        const refreshToken = cookies.RefreshToken;
        if (refreshToken && !isTokenExpired(refreshToken)) {
            try {
                const response = await API.post('/auth/jwt/refresh/', { refresh: refreshToken });
                const newAccessToken = response.data.access;
                setCookie('AccessToken', newAccessToken, { path: '/' });
                return newAccessToken;
            } catch (error) {
                console.error('Error refreshing token:', error);
                logout();
                return null;
            }
        } else {
            logout();
            return null;
        }
    }, [cookies.RefreshToken, setCookie, logout]);




    const [hasChecked, setHasChecked] = useState(false);

    const fetchAuthenticatedPlayer = useCallback(async () => {
        /*
        Main function
        Checks if access token is:
        Invalid? Attempt to refresh access token, if that fails - logout
        Expired? Refresh access token
        */
        try {
            const accessToken = cookies.AccessToken;
            if (accessToken && !isTokenExpired(accessToken)) {
                const isValid = await isTokenValid(accessToken);
                if (isValid) {
                    setIsAuthenticated(true);
                } else {
                    const newToken = await refreshToken();
                    setIsAuthenticated(!!newToken);
                }
            } else {
                if (accessToken) {
                    const newToken = await refreshToken();
                    setIsAuthenticated(!!newToken);
                } else {
                    setIsAuthenticated(false)
                }
            }
        } catch (error) {
            console.error('Error fetching authenticated player:', error);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
            setHasChecked(true);
        }
    }, [cookies, isTokenValid, refreshToken]);

    useEffect(() => {
        if (!hasChecked) {
            fetchAuthenticatedPlayer();
        }
    }, [hasChecked, fetchAuthenticatedPlayer]);


    useEffect(() => {
        /*
        Utility function
        Keeps token refreshed daily for 7 days
        */
        const intervalId = setInterval(async () => {
            await refreshToken();
        }, 24 * 60 * 10 * 1000); // Refresh token every 24 hours
        return () => clearInterval(intervalId);
    }, [refreshToken]);


    return (
        <AuthContext.Provider value={{ login, logout, getToken, register, loading, isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);