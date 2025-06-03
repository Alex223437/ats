import './ManageStrategies.scss';
import SkeletonBlock from '@/components/LoadingComponents/SkeletonBlock/SkeletonBlock';
import FlowerIcon from '@/assets/svg/flower.svg?react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const ManageStrategies = ({ strategies = [], loading, onStart, onStop }) => {
  const hasStrategies = Array.isArray(strategies) && strategies.length > 0;

  return (
    <div className="manage-strategies">
      <h2>My Strategies</h2>

      {loading ? (
        <SkeletonBlock rows={4} />
      ) : !hasStrategies ? (
        <div className="empty-orders empty-strategies">
          <FlowerIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">You don't have any strategies yet.</p>
            <p className="empty-subtext">Create one using the form on the left.</p>
            <Link to="/strategy" className="empty-btn">Go to Strategies</Link>
          </div>
        </div>
      ) : (
        <table className="strategy-table">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Tickers</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy) => (
              <tr key={strategy.id}>
                <td>{strategy.title || 'Untitled'}</td>
                <td>{strategy.tickers?.length ? strategy.tickers.join(', ') : '—'}</td>
                <td>
                  <span className={`status ${strategy.is_enabled ? 'active' : 'inactive'}`}>
                    {strategy.is_enabled ? 'Running' : 'Stopped'}
                  </span>
                </td>
                <td>
                  {strategy.is_enabled ? (
                    <button
                      className="stop"
                      onClick={() => onStop(strategy.id)}
                      aria-label={`Stop strategy ${strategy.title}`}
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      className="start"
                      onClick={() => {
                        if (!strategy.tickers || strategy.tickers.length === 0) {
                          toast.error('Cannot start strategy without assigned tickers.');
                          return;
                        }
                        onStart(strategy.id);
                      }}
                      aria-label={`Start strategy ${strategy.title}`}
                    >
                      Start
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ManageStrategies;