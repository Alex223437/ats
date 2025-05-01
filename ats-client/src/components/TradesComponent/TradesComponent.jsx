import { useState, useEffect } from 'react';
import { getTrades, getOrders, cancelOrder, closePosition, placeOrder } from '../../services/tradeService';
import OrderModal from './CreateOrderModal'; 
import { checkBrokerConnection } from '../../services/userService';
import './TradesComponent.scss';

const TradesComponent = () => {
  const [positions, setPositions] = useState([]);
  const [orders, setOrders] = useState([]);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [connected, setConnected] = useState(null); // null до проверки
  const [connectionMessage, setConnectionMessage] = useState('');

  useEffect(() => {
    const init = async () => {
      const res = await checkBrokerConnection();

      if (res.connected && res.data) {
        setConnected(true);
        loadPositions();
        loadOrders();
      } else {
        setConnected(false);
        setConnectionMessage(res.error || 'Broker not connected');
      }
    };

    init();
  }, []);

  const loadPositions = async () => {
    const data = await getTrades();
    setPositions(data);
  };

  const loadOrders = async () => {
    const data = await getOrders();
    setOrders(data);
  };

  const handleCancelOrder = async (orderId) => {
    if (window.confirm('Are you sure you want to cancel this order?')) {
      await cancelOrder(orderId);
      setOrders(orders.filter((order) => order.id !== orderId));
    }
  };

  const handleClosePosition = async (symbol) => {
    if (window.confirm(`Are you sure you want to close your position in ${symbol}?`)) {
      await closePosition(symbol);
      setPositions(positions.filter((pos) => pos.symbol !== symbol));
    }
  };

  if (connected === false) {
    return (
      <div className="trades-container">
        <h2>❌ Broker not connected</h2>
        <p className="status">{connectionMessage}</p>
      </div>
    );
  }

  return (
    <>
      <div className="trades-container">
        <h2>Open Positions</h2>
        <table className="trades-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
              <th>Average Price</th>
              <th>Current Price</th>
              <th>Change ($)</th>
              <th>Change (%)</th>
              <th>Total Value</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {positions?.length > 0 ? (
              positions.map((pos) => (
                <tr key={`${pos.symbol}-${pos.qty}-${pos.avg_entry_price}`}>
                  <td>{pos.symbol}</td>
                  <td>{pos.qty}</td>
                  <td>${parseFloat(pos.avg_entry_price).toFixed(2)}</td>
                  <td>${parseFloat(pos.current_price).toFixed(2)}</td>
                  <td style={{ color: pos.unrealized_pl > 0 ? 'green' : 'red' }}>
                    ${parseFloat(pos.unrealized_pl).toFixed(2)}
                  </td>
                  <td style={{ color: pos.unrealized_plpc > 0 ? 'green' : 'red' }}>
                    {(parseFloat(pos.unrealized_plpc) * 100).toFixed(2)}%
                  </td>
                  <td>${(pos.qty * pos.current_price).toFixed(2)}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleClosePosition(pos.symbol)}>
                      Close
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8">No open positions</td>
              </tr>
            )}
          </tbody>
        </table>

        {/* New section for displaying orders */}
        <h2>Orders</h2>
        <table className="orders-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Type</th>
              <th>Side</th>
              <th>Quantity</th>
              <th>Filled</th>
              <th>Average Price</th>
              <th>Status</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders?.length > 0 ? (
              orders.map((order) => (
                <tr key={`${order.symbol}-${order.submitted_at}`}>
                  <td>{order.symbol}</td>
                  <td>{order.order_type}</td>
                  <td style={{ color: order.side === 'buy' ? 'green' : 'red' }}>{order.side}</td>
                  <td>{order.qty}</td>
                  <td>{order.filled_qty}</td>
                  <td>
                    {isNaN(parseFloat(order.avg_fill_price))
                      ? '-'
                      : `$${parseFloat(order.avg_fill_price).toFixed(2)}`}
                  </td>
                  <td>{order.status}</td>
                  <td>{new Date(order.submitted_at).toLocaleString()}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleCancelOrder(order.id)}>
                      Cancel
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9">No active orders</td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="create-order-wrapper">
          <button className="create-order-btn" onClick={() => setIsOrderModalOpen(true)}>
            + Create Order
          </button>
        </div>
      </div>
      <OrderModal
        isOpen={isOrderModalOpen}
        onClose={() => setIsOrderModalOpen(false)}
        onOrderPlaced={() => {
          setIsOrderModalOpen(false);
          // Обнови заказы, если нужно сразу отобразить новый:
          getOrders().then(setOrders);
        }}
      />
    </>
  );
};

export default TradesComponent;
