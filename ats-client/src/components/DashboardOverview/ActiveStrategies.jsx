import { Link } from 'react-router-dom';
import OverviewCard from './OverviewCard';
import SkeletonBlock from '@/components/LoadingComponents/SkeletonBlock/SkeletonBlock';
import FlowerIcon from '@/assets/svg/flower.svg?react';
import './DashboardOverview.scss';

const ActiveStrategies = ({ strategies = [], loading }) => {
  const hasStrategies = Array.isArray(strategies) && strategies.length > 0;

  return (
    <OverviewCard title="Active Strategies">
      {loading ? (
        <SkeletonBlock rows={3} />
      ) : hasStrategies ? (
        <table className="table">
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Symbol</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((s) => (
              <tr key={s.id}>
                <td>{s.title}</td>
                <td>{s.ticker}</td>
                <td>
                  <span className={`signal-tag ${s.last_signal?.toLowerCase()}`}>
                    {s.last_signal?.toUpperCase() || '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty-orders empty-strategies">
          <FlowerIcon className="empty-svg empty-svg-fill"/>
          <div className="empty-block">
            <p className="empty-text">No active strategies yet</p>
            <p className="empty-subtext">Create your first strategy to start trading</p>
            <Link to="/strategy" className="empty-btn">Go to Strategies</Link>
          </div>
        </div>
      )}
    </OverviewCard>
  );
};

export default ActiveStrategies;
