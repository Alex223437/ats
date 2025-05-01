import { useState } from 'react';
import { loginUser } from '../../../services/authService';
import { useNavigate, Link } from 'react-router-dom';
import './LoginComponent.scss';

const Login = ({ setUser }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await loginUser(email, password);
      setUser({ email }); // Обновляем состояние юзера
      window.dispatchEvent(new Event('storage')); // Форсим обновление localStorage-событий
      navigate('/'); // Перенаправляем на главную страницу
    } catch (err) {
      setError('Incorrect email or password.');
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      <p className="register-link">
        Don't have an account? <Link to="/register">Sign up</Link>
      </p>
    </div>
  );
};

export default Login;
