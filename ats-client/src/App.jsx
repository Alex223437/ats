import { useState, useEffect, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthContext } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import HeaderComponent from './components/HeaderComponent/HeaderComponent';
import './App.css';

// Lazy pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const LoginComponent = lazy(() => import('./components/AuthComponents/LoginComponent/LoginComponent'));
const RegisterComponent = lazy(() => import('./components/AuthComponents/RegisterComponent/RegisterComponent'));
const StrategyPage = lazy(() => import('./pages/Strategy/StrategyPage'))
const AnalyticsPage = lazy(() => import('./pages/Analytics/AnalyticsPage'));
const BacktestPage = lazy(() => import('./pages/Backtest/BacktestPage'));
const TradingPage = lazy(() => import('./pages/Trading/TradingPage'));
const SettingsPage = lazy(() => import('./pages/Settings/SettingsPage'));

const App = () => {
  const { user, logout, loading } = useAuthContext();
  const [longLoad, setLongLoad] = useState(false);

  useEffect(() => {
    if (loading) {
      const timer = setTimeout(() => setLongLoad(true), 10000); 
      return () => clearTimeout(timer);
    }
  }, [loading]);

  if (loading) {
    return (
      <div className="loading-overlay">
        <LoaderSpinner size={90} color="#c084fc" />
        {longLoad && (
          <p className="loading-text">
            The server is responding slowly. If the page doesn’t load within a minute, please contact the developer.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="App">
      <HeaderComponent user={user} onLogout={logout} />
      <main className="main">
        <Routes>
          <Route path="/" element={user ? <Dashboard /> : <Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginComponent />} />
          <Route path="/register" element={<RegisterComponent />} />
          <Route path="/trades" element={user ? <TradingPage /> : <Navigate to="/login" replace />} />
          <Route path="/settings" element={ user ? (<SettingsPage/>) : <Navigate to="/login" replace />} />
          <Route path="/strategy" element={user ? <StrategyPage /> : <Navigate to="/login" replace />} />
          <Route path="/analytics" element={user ? <AnalyticsPage /> : <Navigate to="/login" replace />} />
          <Route path="/backtest" element={user ? <BacktestPage /> : <Navigate to="/login" replace />} />
        </Routes>
      </main>
      <Toaster position="top-right" toastOptions={{
        duration: 4000,
        style: {
          borderRadius: '12px',
          backdropFilter: 'blur(12px)',
          padding: '16px',
          color: '#f1f5f9',
          fontWeight: 500,
        },
        success: {
          style: {
            background: 'rgba(34, 197, 94, 0.25)',
            border: '1px solid #22c55e',
            boxShadow: '0 8px 20px rgba(34, 197, 94, 0.4)',
          },
        },
        error: {
          style: {
            background: 'rgba(239, 68, 68, 0.25)',
            border: '1px solid #ef4444',
            boxShadow: '0 8px 20px rgba(239, 68, 68, 0.4)',
          },
        },
        blank: {
          style: {
            background: 'rgba(30, 27, 75, 0.4)',
            border: '1px solid #a5b4fc',
            boxShadow: '0 8px 20px rgba(124, 58, 237, 0.2)',
          },
        },
      }} />
    </div>
  );
};

export default App;