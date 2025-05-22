import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import toast from 'react-hot-toast';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import StarIcon from '@/assets/svg/star2.svg?react';
import './RegisterComponent.scss';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });

  const navigate = useNavigate();
  const { registerUser, loading, error } = useAuth();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerUser(formData);
      toast.success('Successfully registered!');
      setTimeout(() => navigate('/login'), 1200);
    } catch (err) {
      console.error(err);
      toast.error(error || 'Registration failed');
    }
  };

  return (
    <div className="register-container">
      <h2>Sign Up</h2>
      <form className="register-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            name="username"
            type="text"
            placeholder="yourname"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Email address</label>
          <input
            name="email"
            type="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            name="password"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Signing up...' : 'Sign Up'}
        </button>

        {loading && <div className="register-loader"><LoaderSpinner /></div>}
      </form>

      <div className="register-icon">
        <StarIcon />
      </div>

      <p className="register-link">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
};

export default Register;