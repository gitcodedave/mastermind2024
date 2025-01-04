import './App.css';
import { AuthProvider } from './context/AuthContext';
import { CookiesProvider } from 'react-cookie';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './routes/routes';


const App = () => {
  return (
    <>
      <div className='main'>
        <CookiesProvider>
          <AuthProvider>
            <BrowserRouter>
              <AppRoutes />
            </BrowserRouter>
          </AuthProvider>
        </CookiesProvider>
      </div>
    </>
  );
}

export default App;
