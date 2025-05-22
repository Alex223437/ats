import OverviewCard from './OverviewCard';
import SkeletonBlock from '@/components/LoadingComponents/SkeletonBlock/SkeletonBlock';
import StarIcon from '@/assets/svg/star3.svg?react';
import './DashboardOverview.scss';

const TickerOverview = ({ tickers = [], loading = false }) => {
  const rows = Array.isArray(tickers) && tickers.length > 0
    ? tickers.filter(t => typeof t === 'object' && t !== null)
    : [];

  if (loading) {
    return (
      <OverviewCard title="Ticker Overview">
        <SkeletonBlock rows={6} />
      </OverviewCard>
    );
  }

  if (rows.length === 0) {
    return (
      <OverviewCard title="Ticker Overview">
        <div className="empty-orders empty-strategies">
          <StarIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">No tickers available</p>
            <p className="empty-subtext">Use the sidebar on the left to add tickers to your profile</p>
          </div>
        </div>
      </OverviewCard>
    );
  }

  return (
    <OverviewCard title="Ticker Overview">
      <table className="table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>RSI</th>
            <th>EMA-10</th>
            <th>Signal</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((t, i) => (
            <tr key={t.symbol || i}>
              <td>{t.symbol || '—'}</td>
              <td>{typeof t.price === 'number' ? `$${t.price.toFixed(2)}` : '—'}</td>
              <td>{typeof t.rsi === 'number' ? t.rsi.toFixed(2) : '—'}</td>
              <td>{typeof t.ema_10 === 'number' ? t.ema_10.toFixed(2) : '—'}</td>
              <td>
                <span className={`signal-tag ${t.signal?.toLowerCase() || 'hold'}`}>
                  {t.signal?.toUpperCase() || '—'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </OverviewCard>
  );
};

export default TickerOverview;


// const mock = [
//     { symbol: 'AAPL', price: 212.33, rsi: 45, ema_10: 133.5, signal: 'BUY' },
//     { symbol: 'MSFT', price: 320.12, rsi: 62, ema_10: 313.4, signal: 'HOLD' },
//     { symbol: 'TSLA', price: 250.87, rsi: 67, ema_10: 245.2, signal: 'SELL' }
//   ];