import { useEffect, useState } from 'react';
import useSettingsApi from '@/hooks/useSettingsApi';
import toast from 'react-hot-toast';

const AccountInfoCard = () => {
  const {
    fetchUserSettings,
    updateUserProfile,
    userSettings,
    loadingUser,
    updatingUser,
  } = useSettingsApi();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => {
    fetchUserSettings();
  }, []);

  useEffect(() => {
    if (userSettings) {
      setUsername(userSettings.username || '');
      setEmail(userSettings.email || '');
    }
  }, [userSettings]);

  const handleSave = async () => {
    try {
      await updateUserProfile({
        username,
        email,
        password: password || undefined,
      });
      setPassword('');
      toast.success('Account updated');
    } catch (err) {
      toast.error('Failed to update profile');
    }
  };

  return (
    <div className="settings-form">
      <h2>Account Information</h2>

      <label>Username</label>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        disabled={loadingUser}
      />

      <label>Email</label>
      <input
        type="text"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={loadingUser}
      />

      <label>New Password</label>
      <input
        type="text"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Leave empty to keep current password"
        disabled={loadingUser}
      />

      <p className="form-warning">
        Registered: {userSettings?.created_at
          ? new Date(userSettings.created_at).toLocaleDateString()
          : '—'}
      </p>

      <div className="button-group">
        <button onClick={handleSave} disabled={updatingUser}>
          {updatingUser ? 'Saving...' : 'Save'}
        </button>
      </div>
    </div>
  );
};

export default AccountInfoCard;