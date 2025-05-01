import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';

const ResetPassword = () => {
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token'); // Получаем токен из URL

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/reset-password', {
        token,
        new_password: newPassword,
      });
      setMessage('Password successfully reset. You can now log in.');
    } catch (error) {
      setMessage('Error: ' + (error.response?.data.detail || 'Something went wrong'));
    }
  };

  return (
    <div>
      <h2>Reset Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <button type="submit">Reset Password</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ResetPassword;
