import { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../services/apiService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const { getCurrentUser, logoutUser } = useAuth();
  const [user, setUser] = useState(undefined); // undefined = loading
  const [loading, setLoading] = useState(true);

  const loadUser = async () => {
    setLoading(true);
    const userData = await getCurrentUser();
    setUser(userData); // null если неавторизован
    setLoading(false);
  };

  const logout = () => {
    logoutUser();
    setUser(null);
  };

  useEffect(() => {
    loadUser();

    // автообновление токена каждые 5 минут
    const refreshInterval = setInterval(() => {
      api.get('/refresh').catch(() => {
        // если refresh не сработал — разлогиниваем
        setUser(null);
      });
    }, 1000 * 60 * 5); // каждые 5 минут

    const handleStorageChange = () => {
      if (localStorage.getItem('token')) loadUser();
      else setUser(null);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => {
      clearInterval(refreshInterval);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, setUser, logout, isAuthenticated: !!user, loading, loadUser }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => useContext(AuthContext);