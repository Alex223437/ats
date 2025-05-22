import { useState } from 'react';
import OverviewCard from './OverviewCard';
import SkeletonBlock from '@/components/LoadingComponents/SkeletonBlock/SkeletonBlock';
import TelephoneIcon from '@/assets/svg/telephone.svg?react';
import './DashboardOverview.scss';

const ITEMS_PER_PAGE = 4;

const RecentSignals = ({ signals = [], loading }) => {
  const [page, setPage] = useState(1);

  if (loading) {
    return (
      <OverviewCard title="Recent Signals">
        <SkeletonBlock rows={4} />
      </OverviewCard>
    );
  }

  const items = Array.isArray(signals) && signals.length > 0 ? signals : [];
  const totalPages = Math.ceil(items.length / ITEMS_PER_PAGE);
  const paginated = items.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  if (items.length === 0) {
    return (
      <OverviewCard title="Recent Signals">
        <div className="empty-orders empty-strategies">
          <TelephoneIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">No recent signals</p>
            <p className="empty-subtext">Signals will appear here when your strategies generate them.</p>
          </div>
        </div>
      </OverviewCard>
    );
  }

  return (
    <OverviewCard title="Recent Signals">
      <table className="table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Action</th>
            <th>Strategy</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {paginated.map((signal, index) => (
            <tr key={index}>
              <td>{signal.ticker || "—"}</td>
              <td>
                <span className={`signal-tag ${signal.action?.toLowerCase() || 'hold'}`}>
                  {signal.action?.toUpperCase() || "—"}
                </span>
              </td>
              <td>{signal.strategy_title || "—"}</td>
              <td>
                {signal.created_at
                  ? new Date(signal.created_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {totalPages > 1 && (
        <div className="pagination-controls">
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={`page-btn ${page === i + 1 ? 'active' : ''}`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </OverviewCard>
  );
};

export default RecentSignals;