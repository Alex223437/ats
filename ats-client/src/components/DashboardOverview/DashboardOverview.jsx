import ActiveStrategies from './ActiveStrategies';
import TickerOverview from './TickerOverview';
import BrokerStatus from './BrokerStatus';
import RecentSignals from './RecentSignals';
import MiniChart from './MiniChart';
import useDashboardApi from '@/hooks/useDashboardApi';
import './DashboardOverview.scss';

const DashboardOverview = ({ selectedStock, stocks }) => {
  const {
    loading,
    data: {
      flattenedStrategies,
      tickerData,
      brokerInfo,
      recentSignals,
      miniChartData
    },
  } = useDashboardApi(selectedStock, stocks);

  return (
    <div className="dashboard-grid">
      <ActiveStrategies
        strategies={flattenedStrategies}
        loading={loading.strategies}
      />

      <TickerOverview
        tickers={tickerData || []}
        loading={loading.overview}
      />

      <MiniChart
        ticker={selectedStock}
        data={miniChartData}
        loading={loading.chart}
      />

      <BrokerStatus
        broker={brokerInfo}
        loading={loading.broker}
        setBrokerInfo={() => {}}
      />

      <RecentSignals
        signals={recentSignals || []}
        loading={loading.signals}
      />
    </div>
  );
};

export default DashboardOverview;