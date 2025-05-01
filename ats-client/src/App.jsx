import { useState, useEffect, lazy } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';



import ChartComponent from './components/ChartComponent/ChartComponent';
import HeaderComponent from './components/HeaderComponent/HeaderComponent';
import AsideDashboard from './components/AsideComponent/AsideDashboard';
import Dashboard from './pages/Dashboard';
import ActiveStrategiesPanel from './components/StrategyComponent/AcitveStrategiesPanel';


const LoginComponent = lazy(
  () => import('./components/AuthComponents/LoginComponent/LoginComponent')
);
const RegisterComponent = lazy(
  () => import('./components/AuthComponents/RegisterComponent/RegisterComponent')
);
const TradesComponent = lazy(() => import('./components/TradesComponent/TradesComponent'));
const SettingsComponent = lazy(() => import('./components/SettingsComponent/SettingsPage'));
const AsideSettings = lazy(() => import('./components/AsideComponent/AsideSettings'));
const StrategyPage = lazy(() => import('./components/StrategyComponent/StrategyPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));

import { getCurrentUser, logoutUser } from './services/authService';

import './App.css';

const App = () => {
  const [user, setUser] = useState(undefined);
  const [selectedSection, setSelectedSection] = useState('Profile');

  useEffect(() => {
    let isMounted = true;

    const fetchUser = async () => {
      const userData = await getCurrentUser();
      if (isMounted) {
        setUser(userData); // Устанавливаем null, если юзер не аутентифицирован
      }
    };

    fetchUser();

    const handleStorageChange = () => {
      if (localStorage.getItem('token')) {
        fetchUser();
      } else {
        setUser(null); // Если токен удалён, сразу обнуляем юзера
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      isMounted = false;
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    logoutUser();
    setUser(null);
  };

  if (user === undefined) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <HeaderComponent user={user} onLogout={handleLogout} />
        <main className="main">
          <Routes>
            <Route
              path="/"
              element={
                user ? (
                  <Dashboard></Dashboard>
                ) : user === null ? (
                  <Navigate to="/login" replace />
                ) : (
                  <div>Loading...</div>
                )
              }
            />
            <Route path="/login" element={<LoginComponent setUser={setUser} />} />
            <Route path="/register" element={<RegisterComponent />} />
            <Route
              path="/trades"
              element={user ? <TradesComponent /> : <Navigate to="/login" replace />}
            />
            <Route
              path="/settings"
              element={
                user ? (
                  <>
                    <AsideSettings
                      selectedSection={selectedSection}
                      setSelectedSection={setSelectedSection}
                    />
                    <SettingsComponent selectedSection={selectedSection} />
                  </>
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/strategy"
              element={user ? <StrategyPage /> : <Navigate to="/login" replace />}
            />
            <Route
              path="/analytics"
              element={user ? <AnalyticsPage /> : <Navigate to="/login" replace />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
