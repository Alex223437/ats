import { useEffect, useState } from 'react';
import {
  updateBrokerSettings,
  getUserSettings,
  checkBrokerConnection,
  disconnectBroker
} from '../../services/userService';
import './SettingsAPI.scss';

const SettingsAPI = () => {
  const [broker, setBroker] = useState('alpaca');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [accountInfo, setAccountInfo] = useState(null);

  useEffect(() => {
    const init = async () => {
      const result = await checkBrokerConnection();
      if (result.connected) {
        setConnected(true);
        setAccountInfo(result.data);
      } else {
        setConnected(false);
        const data = await getUserSettings();
        if (data) {
          setApiKey(data.alpaca_api_key || '');
          setApiSecret(data.alpaca_api_secret || '');
          setBaseUrl(data.alpaca_base_url || '');
        }
        setMessage(result.error || '');
      }
    };

    init();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setMessage('');

    const result = await updateBrokerSettings({
      broker,
      api_key: apiKey,
      api_secret: apiSecret,
      base_url: baseUrl,
    });

    if (result.success) {
      const check = await checkBrokerConnection();
      if (check.connected && check.data?.account_status && check.data?.cash !== undefined) {
        setConnected(true);
        setAccountInfo(check.data);
        setMessage('✅ Connected!');
      } else {
        setMessage('✅ Keys updated, but not connected. Please check your API keys.');
      }
    } else {
      setMessage('❌ Failed to save settings. Please check your API keys.');
    }

    setLoading(false);
  };

  const handleDisconnect = async () => {
    const confirmed = window.confirm('Are you sure you want to disconnect your broker?');
    if (!confirmed) return;

    const result = await disconnectBroker();
    if (result.success) {
      setApiKey('');
      setApiSecret('');
      setBaseUrl('');
      setConnected(false);
      setAccountInfo(null);
      setMessage('🔌 Broker disconnected');
    } else {
      setMessage('❌ Failed to disconnect broker');
    }
  };

  return (
    <>
      <h2>API Broker Settings</h2>
  
      {connected ? (
        <>
          <p className="message">
            ✅ Connected to Alpaca — <strong>{accountInfo.account_status}</strong>, Cash: ${parseFloat(accountInfo.cash).toFixed(2)}
          </p>
          <button onClick={handleDisconnect}>
            ❌ Disconnect Broker
          </button>
        </>
      ) : (
        <div className="settings-form">
          <label>Choose Broker</label>
          <select value={broker} onChange={(e) => setBroker(e.target.value)}>
            <option value="alpaca">Alpaca</option>
          </select>
  
          <label>API Key</label>
          <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
  
          <label>API Secret</label>
          <input value={apiSecret} onChange={(e) => setApiSecret(e.target.value)} type="password" />
  
          <label>Base URL</label>
          <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
  
          <button onClick={handleSave} disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </button>
  
          {message && <p className="message">{message}</p>}
        </div>
      )}
    </>
  );
};

export default SettingsAPI;