import { useState } from "react";
import { useAuth } from '../context/AuthContext';
import { Navigate } from "react-router-dom";


const LoginBox = () => {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loggedIn, setLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('')
    const { login, getToken } = useAuth();

    const handleLoginClick = async (e) => {
        /*
        Passes credentials to auth for authenticating user
        Updates cookies and navigates user to game page
        */
        e.preventDefault();
        setIsLoading(true)
        const credentials = {
            username: username,
            password: password
        }

        const token = await getToken(credentials);

        if (token) {
            const accessToken = token.access;
            const refreshToken = token.refresh;
            login(credentials.username, accessToken, refreshToken);
            setLoggedIn(true);
        } else {
            let allForms = document.querySelectorAll('input');
            allForms.forEach(eachInput => eachInput.value = '');
            setError('Invalid username or password');
            setIsLoading(false)
        }
    }

    if (loggedIn) {
        return <Navigate to='/game' />;
    }

    return (
        <div>
            <div className='errormessage'>
                {error}
            </div>
            <form className='loginregisterbox'>
                <div>
                    Login
                </div>
                <input
                    className='loginregisterinput'
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="username"
                    type='text'>
                </input>

                <input
                    className='loginregisterinput'
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="password"
                    type='password'>
                </input>
                <button className='submitbutton' onClick={handleLoginClick} type='submit'>submit</button>
            </form>
            {isLoading && <div className='loading'>Loading...</div>}
        </div>
    )
}

export default LoginBox;