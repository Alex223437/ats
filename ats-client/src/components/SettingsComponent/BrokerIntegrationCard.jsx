import { useEffect, useState } from 'react';
import useSettingsApi from '@/hooks/useSettingsApi';
import toast from 'react-hot-toast';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';

const BrokerIntegrationCard = () => {
  const {
    fetchBroker,
    updateBroker,
    disconnectBroker,
    brokerData,
    loadingBroker,
    updatingBroker,
    disconnectingBroker,
  } = useSettingsApi();

  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://paper-api.alpaca.markets');
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetchBroker().then((res) => {
      if (res?.connected) {
        setConnected(true);
        setApiKey('••••••••••••');
        setApiSecret('••••••••••••');
        setBaseUrl(res.base_url || baseUrl);
      } else {
        setConnected(false);
      }
    });
  }, []);

  const handleConnect = async () => {
    try {
      await updateBroker({
        broker: 'alpaca',
        api_key: apiKey,
        api_secret: apiSecret,
        base_url: baseUrl,
      });
      toast.success('Broker connected');
      setConnected(true);
    } catch {
      toast.error('Failed to connect broker');
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Disconnect broker?')) return;
    try {
      await disconnectBroker('alpaca');
      toast.success('Broker disconnected');
      setConnected(false);
      setApiKey('');
      setApiSecret('');
    } catch {
      toast.error('Failed to disconnect broker');
    }
  };

  if (loadingBroker) {
    return (
      <div className="settings-form broker-form">
        <h2>Broker Integration</h2>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '1.5rem 0' }}>
          <LoaderSpinner size={60} color="#a78bfa" />
        </div>
      </div>
    );
  }

  return connected ? (
    <div className="broker-card-connected">
      <div className="broker-header">
        <h3>Alpaca</h3>
        <span className="status-tag">Connected</span>
      </div>
      <div className="broker-actions">
        <button onClick={handleDisconnect} disabled={disconnectingBroker}>
          {disconnectingBroker ? 'Disconnecting...' : 'Disconnect'}
        </button>
      </div>
    </div>
  ) : (
    <form className="settings-form broker-form">
      <h2>Broker Integration</h2>

      <label>API Key</label>
      <input
        type="text"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        disabled={updatingBroker || disconnectingBroker}
      />

      <label>API Secret</label>
      <input
        type="password"
        value={apiSecret}
        onChange={(e) => setApiSecret(e.target.value)}
        disabled={updatingBroker || disconnectingBroker}
      />

      <label>Base URL</label>
      <input
        type="text"
        value={baseUrl}
        onChange={(e) => setBaseUrl(e.target.value)}
        disabled={updatingBroker || disconnectingBroker}
      />

      <div className="button-group">
        <button onClick={handleConnect} disabled={updatingBroker}>
          {updatingBroker ? 'Connecting...' : 'Connect'}
        </button>
      </div>
    </form>
  );
};

export default BrokerIntegrationCard;