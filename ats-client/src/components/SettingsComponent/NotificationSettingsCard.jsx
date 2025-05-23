import { useEffect, useState } from 'react';
import useSettingsApi from '@/hooks/useSettingsApi';
import toast from 'react-hot-toast';

const NotificationSettingsCard = () => {
  const {
    fetchNotifications,
    updateNotifications,
    notificationSettings,
    loadingNotifications,
    updatingNotifications,
  } = useSettingsApi();

  const [emailAlerts, setEmailAlerts] = useState(false);
  const [onSignal, setOnSignal] = useState(false);
  const [onOrderFilled, setOnOrderFilled] = useState(false);
  const [onError, setOnError] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  useEffect(() => {
    if (notificationSettings) {
      setEmailAlerts(notificationSettings.email_alerts_enabled);
      setOnSignal(notificationSettings.notify_on_signal);
      setOnOrderFilled(notificationSettings.notify_on_order_filled);
      setOnError(notificationSettings.notify_on_error);
    }
  }, [notificationSettings]);

  const handleSave = async () => {
    try {
      await updateNotifications({
        email_alerts_enabled: emailAlerts,
        notify_on_signal: onSignal,
        notify_on_order_filled: onOrderFilled,
        notify_on_error: onError,
      });
      toast.success('Notification settings saved');
    } catch {
      toast.error('Failed to save notification settings');
    }
  };

  return (
    <form className="settings-form">
      <h2>Notification Settings</h2>

      <label>Email Alerts</label>
      <div className="notification-toggle-group">
        <div
          className={`toggle-button ${emailAlerts ? 'active' : ''}`}
          onClick={() => setEmailAlerts(true)}
        >
          On
        </div>
        <div
          className={`toggle-button ${!emailAlerts ? 'active' : ''}`}
          onClick={() => setEmailAlerts(false)}
        >
          Off
        </div>
      </div>

      <label>
        <input
          type="checkbox"
          checked={onSignal}
          onChange={(e) => setOnSignal(e.target.checked)}
        />{' '}
        On Signal
      </label>

      <label>
        <input
          type="checkbox"
          checked={onOrderFilled}
          onChange={(e) => setOnOrderFilled(e.target.checked)}
        />{' '}
        On Order Filled
      </label>

      <label>
        <input
          type="checkbox"
          checked={onError}
          onChange={(e) => setOnError(e.target.checked)}
        />{' '}
        On Error
      </label>

      <div className="button-group">
        <button type="button" onClick={handleSave} disabled={updatingNotifications}>
          {updatingNotifications ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
};

export default NotificationSettingsCard;