import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { useAuthContext } from '@/context/AuthContext';
import CloudIcon from '@/assets/svg/cloud.svg?react';
import toast from 'react-hot-toast';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import EyeIcon from '@/assets/svg/eye.svg?react';
import './LoginComponent.scss';

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const { loginUser, loading, error } = useAuth();
  const { loadUser } = useAuthContext();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await loginUser(email, password);
      await loadUser();
      toast.success('Logged in successfully!');
      navigate('/');
    } catch (err) {
      console.error(err);
      toast.error(error || 'Login failed');
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin} className="login-form">
        <div className="form-group">
          <label>Email or Username</label>
          <input
            id="email"
            type="text"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-group password-group">
          <label>Password</label>
          <div className="password-wrapper">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="eye-toggle"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label="Toggle password visibility"
            >
              <EyeIcon />
            </button>
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>Login</button>
        {loading ? <div className='login-loader'><LoaderSpinner/></div>: null}
        {error && <p className="error-message">{error}</p>}
      </form>

      <div className="login-icon">
        <CloudIcon />
      </div>

      <p className="register-link">
        Don't have an account? <Link to="/register">Sign up</Link>
      </p>
    </div>
  );
};

export default Login;