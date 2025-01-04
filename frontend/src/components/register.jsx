import { useState } from "react";
import { useAuth } from '../context/AuthContext';
import { Navigate } from "react-router-dom";

const RegisterBox = () => {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loggedIn, setLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('')
    const { login, getToken, register } = useAuth();

    const handleRegisterClick = async (e) => {
        /*
        Passes credentials to auth for registering user
        Updates cookies and navigates user to game page
        */
        e.preventDefault()
        setError('')
        setIsLoading(true)

        const credentials = {
            username: username,
            password: password
        }

        const registerResponse = await register(credentials);
        if (registerResponse.status === 201) {
            const token = await getToken(credentials);
            const accessToken = token.access
            const refreshToken = token.refresh
            login(credentials.username, accessToken, refreshToken);
            setLoggedIn(true);
        }
        if (registerResponse.status === 400) {
            setIsLoading(false)
            const errorType = registerResponse.data
            if (errorType.username) {
                setError(`(${errorType.username[0]})`)
                return;
            } else if (errorType.password) {
                setError(`(${errorType.password[0]})`)
                return;
            }
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
                    Register
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
                <button className='submitbutton' onClick={handleRegisterClick} type='submit'>submit</button>
            </form>
            {isLoading && <div className='loading'>Loading...</div>}
        </div>
    )
}

export default RegisterBox;