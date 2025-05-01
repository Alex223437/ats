import { useState, useEffect } from 'react';
import { getUserSettings, updateUserProfile } from '../../services/userService';

const SettingsProfile = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const loadSettings = async () => {
      const data = await getUserSettings();
      if (data) {
        setUsername(data.username);
        setEmail(data.email);
      }
    };
    loadSettings();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    const result = await updateUserProfile({ username, email, password });
    if (result.success) {
      setMessage('✅ Settings updated successfully!');
    } else {
      setMessage('❌ Failed to update settings');
    }
    setLoading(false);
  };

  return (
    <div className="settings-profile">
      <h2>Profile Settings</h2>
      <div className="settings-form">
        <label>Username</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />

        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />

        <label>New Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter new password (optional)"
        />

        <button onClick={handleSave} disabled={loading}>
          {loading ? 'Saving...' : 'Save Changes'}
        </button>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
};

export default SettingsProfile;
