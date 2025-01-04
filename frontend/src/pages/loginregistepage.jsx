import { useState } from "react";
import LoginBox from "../components/login";
import RegisterBox from "../components/register";

const LoginRegisterPage = () => {
    /*
    Loads either login or register component based on user selection
    */
    const [loginPage, setLoginPage] = useState(true)

    return (
        <div className="loginregistercontainer">
            <div className='gametitle'>
                MASTERMIND
            </div>
            {loginPage && (
                <div>
                    <LoginBox />
                    <div className='register' style={{ marginTop: '20px' }}>
                        Need to Register? <button onClick={(e) => setLoginPage(!loginPage)}>Register</button>
                    </div>
                </div>
            )}

            {!loginPage && (
                <div>
                    <RegisterBox />
                    <div className='register' style={{ marginTop: '20px' }}>
                        Back to Login <button onClick={(e) => setLoginPage(!loginPage)}>Back</button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default LoginRegisterPage;