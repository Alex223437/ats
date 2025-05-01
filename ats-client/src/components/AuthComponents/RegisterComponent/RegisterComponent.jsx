import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './RegisterComponent.scss';

const API_URL = 'http://localhost:8000'; // Обнови, если сервер работает на другом хосте

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });

  const [message, setMessage] = useState('');
  const navigate = useNavigate(); // Добавляем навигацию

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/register`, formData);
      setMessage(response.data.message);

      // ✅ После успешной регистрации сразу перенаправляем на страницу логина
      setTimeout(() => {
        navigate('/login');
      }, 2000); // Ждем 2 секунды перед редиректом
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error');
    }
  };

  return (
    <div className="register-container">
    <h2>Sign Up</h2>
    <form onSubmit={handleSubmit}>
      <input
        name="username"
        type="text"
        placeholder="Username"
        value={formData.username}
        onChange={handleChange}
        required
      />
      <input
        name="email"
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      <input
        name="password"
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={handleChange}
        required
      />
      <button type="submit">Sign Up</button>
    </form>
    {message && <p className="error">{message}</p>}

    <p className="register-link">
      Already have an account? <Link to="/login">Log in</Link>
    </p>
  </div>
  );
};

export default Register;
