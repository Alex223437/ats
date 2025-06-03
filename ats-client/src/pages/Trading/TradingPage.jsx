import { useNavigate } from 'react-router-dom';
import TradeForm from '@/components/TradesComponent/TradeForm';
import OrdersTable from '@/components/TradesComponent/OrdersTable';
import PositionsTable from '@/components/TradesComponent/PositionsTable';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import StarIcon from '@/assets/svg/star1.svg?react';
import useTradingApi from '@/hooks/useTradingApi';
import toast from 'react-hot-toast';
import './TradingPage.scss';

const TradingPage = () => {
  const navigate = useNavigate();

  const {
    connected,
    brokerError,
    initialLoaded,
    orders,
    positions,
    loadingOrders,
    loadingPositions,
    fetchOrders,
    fetchPositions,
  } = useTradingApi();

  const handleOrderCancel = async (id) => {
    try {
      await fetchOrders({ method: 'delete', url: `/orders/${id}` });
      toast.success('Order canceled');
      await fetchOrders({ method: 'get', url: '/orders' });
    } catch {
      toast.error('Failed to cancel order');
    }
  };

  const handlePositionClose = async (symbol) => {
    try {
      await fetchPositions({ method: 'delete', url: `/trades/${symbol}` });
      toast.success(`Position ${symbol} closed`);
      await fetchPositions({ method: 'get', url: '/trades' });
    } catch {
      toast.error(`Failed to close position ${symbol}`);
    }
  };

  if (connected === null) {
    return (
      <div className="loading-overlay">
        <LoaderSpinner size={90} color="#c084fc" />
        <p className="loading-text">
          The server is responding slowly. If the page doesn’t load within a minute, please contact the developer.
        </p>
      </div>
    );
  }

  if (connected === false) {
    return (
      <div className="broker-error-container">
        <StarIcon className="broker-error-icon" />
        <h2>Broker not connected</h2>
        <p>{brokerError || 'Please connect your broker account in settings to start trading.'}</p>
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
        orders={orders}
        loading={!initialLoaded || loadingOrders}
        onCancel={handleOrderCancel}
      />

      <PositionsTable
        positions={positions}
        loading={!initialLoaded || loadingPositions}
        onClose={handlePositionClose}
      />
    </div>
  );
};

export default TradingPage;