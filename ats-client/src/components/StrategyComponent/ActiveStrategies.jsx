import './ActiveStrategies.scss';
import OverviewCard from '../DashboardOverview/OverviewCard';
import RectangleIcon from '@/assets/svg/rectangle.svg?react';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import { Link } from 'react-router-dom';

const ActiveStrategies = ({ strategies = [], loading, onStop, onViewLogs }) => {
  const activeStrategies = strategies.filter((s) => s.is_enabled);

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    const date = new Date(isoString);
    return date.toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <OverviewCard title="Active Strategies">
      {loading ? (
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: '10px', color: '#94a3b8' }}>Loading active strategies...</p>
        </div>
      ) : activeStrategies.length === 0 ? (
        <div className="empty-orders empty-strategies">
          <RectangleIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">You have no active strategies running.</p>
            <p className="empty-subtext">Start one using the list below.</p>
            <Link to="/strategy" className="empty-btn">Manage Strategies</Link>
          </div>
        </div>
      ) : (
        <div className="active-strategies-list">
          {activeStrategies.map((s) => (
            <div key={s.id} className="active-strategy-card">
              <div className="strategy-header">
                <h4>{s.title}</h4>
                <span className="status-tag running">Running</span>
              </div>

              <div className="details">
                <p><strong>Tickers:</strong> {s.tickers?.join(', ') || '—'}</p>
                <p><strong>Signal Logic:</strong> {s.signal_logic}</p>
                <p><strong>Last Checked:</strong> {formatDate(s.last_checked) || "—"}</p>
                <p><strong>Last Signal:</strong> {
                  Object.entries(s.last_signals || {}).map(([ticker, signal]) => (
                    <span key={ticker}>{ticker}: {signal}&nbsp;</span>
                  ))
                }</p>
              </div>

              <div className="actions">
                <button className="stop" onClick={() => onStop(s.id)}>
                  Stop
                </button>
                <button className="logs" onClick={() => onViewLogs(s.id)}>
                  View Log
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </OverviewCard>
  );
};

export default ActiveStrategies;