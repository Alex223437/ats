import OverviewCard from '../DashboardOverview/OverviewCard';
import SkeletonBlock from '../LoadingComponents/SkeletonBlock/SkeletonBlock';
import SunIcon from '@/assets/svg/sun.svg?react';

const OrdersTable = ({ orders, loading, onCancel }) => {
  const hasOrders = orders && orders.length > 0;

  return (
    <OverviewCard title="Orders">
      {loading ? (
        <SkeletonBlock />
      ) : hasOrders ? (
        <table className="table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Type</th>
              <th>Side</th>
              <th>Quantity</th>
              <th>Filled</th>
              <th>Avg Price</th>
              <th>Status</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={`${order.symbol}-${order.submitted_at}`}>
                <td>{order.symbol}</td>
                <td>{order.order_type}</td>
                <td style={{ color: order.side === 'buy' ? 'green' : 'red' }}>{order.side}</td>
                <td>{order.qty}</td>
                <td>{order.filled_qty}</td>
                <td>
                  {isNaN(parseFloat(order.avg_fill_price)) ? '-' : `$${parseFloat(order.avg_fill_price).toFixed(2)}`}
                </td>
                <td>{order.status}</td>
                <td>{new Date(order.submitted_at).toLocaleString()}</td>
                <td>
                  <button className="delete-btn" onClick={() => onCancel(order.id)}>Cancel</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty-orders">
          <SunIcon className="empty-svg" />
          <div className="empty-block">
            <p className="empty-text">You have no active orders.</p>
            <p className="empty-subtext">Use the form on the left to create one.</p>
          </div>
        </div>
      )}
    </OverviewCard>
  );
};

export default OrdersTable;