import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TradeForm from '@/components/TradesComponent/TradeForm';
import OrdersTable from '@/components/TradesComponent/OrdersTable';
import PositionsTable from '@/components/TradesComponent/PositionsTable';
import { useBrokerApi } from '@/hooks/useBrokerApi';
import useApiRequest from '@/hooks/useApiRequest';
import StarIcon from '@/assets/svg/star1.svg?react';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import toast from 'react-hot-toast';
import './TradingPage.scss';

const TradingPage = () => {
  const navigate = useNavigate();
  const defaultBroker = 'alpaca';

  const [connected, setConnected] = useState(null); // null → инициализация
  const [message, setMessage] = useState('');
  const [longLoad, setLongLoad] = useState(false);

  const { checkBroker } = useBrokerApi();

  const {
    data: orders,
    loading: loadingOrders,
    request: fetchOrders
  } = useApiRequest();

  const {
    data: positions,
    loading: loadingPositions,
    request: fetchPositions
  } = useApiRequest();

  useEffect(() => {
    const timer = setTimeout(() => setLongLoad(true), 8000);

    const load = async () => {
      try {
        const res = await checkBroker(defaultBroker);
        if (res.connected) {
          setConnected(true);
          await fetchOrders({ method: 'get', url: '/orders' });
          await fetchPositions({ method: 'get', url: '/trades' });
        } else {
          setConnected(false);
          setMessage(res.error || 'Broker not connected');
        }
      } catch (err) {
        setConnected(false);
        setMessage('Failed to verify broker connection');
      } finally {
        clearTimeout(timer);
      }
    };

    load();
  }, []);

  // Пока идёт первичная проверка → показываем прелоадер
  if (connected === null) {
    return (
      <div className="loading-overlay">
        <LoaderSpinner size={90} color="#c084fc" />
        {longLoad && (
          <p className="loading-text">
            The server is responding slowly. If the page doesn’t load within a minute, please contact the developer.
          </p>
        )}
      </div>
    );
  }

  if (connected === false) {
    return (
      <div className="broker-error-container">
        <StarIcon className="broker-error-icon" />
        <h2>Broker not connected</h2>
        <p>{message || 'Please connect your broker account in settings to start trading.'}</p>
        <button className="go-settings-btn" onClick={() => navigate('/settings')}>
          Go to Settings
        </button>
      </div>
    );
  }

  return (
    <div className="trading-grid">
      <TradeForm onOrderPlaced={() => fetchOrders({ method: 'get', url: '/orders' })} />

      <OrdersTable
        orders={orders || []}
        loading={loadingOrders}
        onCancel={async (id) => {
          try {
            await fetchOrders({ method: 'delete', url: `/orders/${id}` });
            toast.success('Order canceled', { id: `cancel-order-${id}` });
            await fetchOrders({ method: 'get', url: '/orders' });
          } catch {
            toast.error('Failed to cancel order', { id: `cancel-order-${id}` });
          }
        }}
      />

      <PositionsTable
        positions={positions || []}
        loading={loadingPositions}
        onClose={async (symbol) => {
          try {
            await fetchPositions({ method: 'delete', url: `/trades/${symbol}` });
            toast.success(`Position ${symbol} closed`, { id: `close-${symbol}` });
            await fetchPositions({ method: 'get', url: '/trades' });
          } catch {
            toast.error(`Failed to close position ${symbol}`, { id: `close-${symbol}` });
          }
        }}
      />
    </div>
  );
};

export default TradingPage;