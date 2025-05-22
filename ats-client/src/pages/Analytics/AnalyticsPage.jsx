import React, { useState, useEffect } from 'react';
import useAnalyticsData from '../../hooks/useAnalyticsData';
import AsideFiltersAnalytics from '../../components/AsideComponent/AsideFiltersAnalytics';
import KpiCards from '../../components/AnalyticsComponent/KpiCards';
import EquityCurveChart from '../../components/AnalyticsComponent/EquityCurveChart';
import PnLByTickerChart from '../../components/AnalyticsComponent/PnlByTickerChart';
import TradesTable from '../../components/AnalyticsComponent/TradesTable';
import './AnalyticsPage.scss';

const AnalyticsPage = () => {
  const [filters, setFilters] = useState(null);
  const {
    overview,
    strategiesPnl,
    topTickers,
    equityCurve,
    trades,
    fetchOverview,
    fetchStrategiesPnl,
    fetchTopTickers,
    fetchEquityCurve,
    fetchTrades,
  } = useAnalyticsData();

  useEffect(() => {
    if (!filters) return;
    fetchOverview(filters);
    fetchStrategiesPnl(filters);
    fetchTopTickers(filters);
    fetchEquityCurve(filters);
    fetchTrades(filters);
  }, [filters]);

  return (
    <div className="analytics-grid">
      <AsideFiltersAnalytics
        onApply={(filters) => setFilters(filters)}
      />

      <KpiCards data={overview.data} />

      <EquityCurveChart data={equityCurve.data} loading={equityCurve.loading}/>
      <PnLByTickerChart data={topTickers.data} loading={topTickers.loading}/>
      <TradesTable trades={trades.data} loading={trades.loading}/>

    </div>
  );
};

export default AnalyticsPage;