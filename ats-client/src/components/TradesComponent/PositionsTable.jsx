import OverviewCard from '../DashboardOverview/OverviewCard';
import SkeletonBlock from '../LoadingComponents/SkeletonBlock/SkeletonBlock';
import FlowerIcon from '@/assets/svg/flower.svg?react';

const PositionsTable = ({ positions, loading, onClose }) => {
  const hasPositions = positions && positions.length > 0;

  return (
    <OverviewCard title="Open Positions">
      {loading ? (
        <SkeletonBlock />
      ) : hasPositions ? (
        <table className="table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
              <th>Avg Price</th>
              <th>Current Price</th>
              <th>Change ($)</th>
              <th>Change (%)</th>
              <th>Total Value</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
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
                  <button className="delete-btn" onClick={() => onClose(pos.symbol)}>Close</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty-orders">
          <FlowerIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">You have no open positions.</p>
            <p className="empty-subtext">Trade some stocks using the form on the left.</p>
          </div>
        </div>
      )}
    </OverviewCard>
  );
};

export default PositionsTable;