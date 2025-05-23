import { useEffect, useState } from 'react';
import useBrokerApi from '@/hooks/useBrokerApi';
import './SettingsAPI.scss';

const SettingsAPI = () => {
  const [broker, setBroker] = useState('alpaca');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [message, setMessage] = useState('');
  const [connected, setConnected] = useState(false);
  const [accountInfo, setAccountInfo] = useState(null);

  const { checkState, updateBroker, disconnectBroker, checkBroker, loading } = useBrokerApi();

  useEffect(() => {
    const init = async () => {
      const result = await checkBroker(broker);
      if (result.connected) {
        setConnected(true);
        setAccountInfo(result);
      } else {
        setConnected(false);
        const fallback = await checkState(); // legacy fallback
        if (fallback) {
          setApiKey(fallback.alpaca_api_key || '');
          setApiSecret(fallback.alpaca_api_secret || '');
          setBaseUrl(fallback.alpaca_base_url || '');
        }
        setMessage(result.error || '');
      }
    };

    init();
  }, [broker]);

  const handleSave = async () => {
    setMessage('');
    const result = await updateBroker({
      broker,
      api_key: apiKey,
      api_secret: apiSecret,
      base_url: baseUrl
    });

    if (result.success) {
      const check = await checkBroker(broker);
      if (check.connected && check.account_status && check.cash !== undefined) {
        setConnected(true);
        setAccountInfo(check);
        setMessage('✅ Connected!');
      } else {
        setMessage('✅ Keys updated, but not connected. Please check your API keys.');
      }
    } else {
      setMessage('❌ Failed to save settings. Please check your API keys.');
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect your broker?')) return;

    const result = await disconnectBroker(broker);
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
          <button onClick={handleDisconnect}>❌ Disconnect Broker</button>
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