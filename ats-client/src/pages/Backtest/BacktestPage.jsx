import React, { useState } from 'react';
import AsideBacktest from '../../components/AsideComponent/AsideBacktest';
import KpiCards from '../../components/AnalyticsComponent/KpiCards';
import BacktestEquityChart from '../../components/BacktestComponents/BacktestEquityChart';
import BacktestTradesTable from '../../components/BacktestComponents/BacktestTradesTable';
import useBacktestApi from '@/hooks/useBacktestApi';
import './BacktestPage.scss';

const BacktestPage = () => {

  const { runBacktest, run } = useBacktestApi();
  const result = run.data;
  const loading = run.loading;

  const handleBacktestRun = async (params) => {
    if (!params?.start_date || !params?.end_date) return;

    const safeStart = new Date(params.start_date);
    const safeEnd = new Date(params.end_date);

    if (isNaN(safeStart.getTime()) || isNaN(safeEnd.getTime())) return;

    await runBacktest({
      ...params,
      start_date: safeStart.toISOString(),
      end_date: safeEnd.toISOString(),
    });
  };
  return (
    <div className="backtest-grid">
      <AsideBacktest onRun={handleBacktestRun} />
      <KpiCards data={result?.metrics} loading={loading} />
      <BacktestEquityChart data={result?.equity_curve} loading={loading} />
      <BacktestTradesTable trades={result?.trades} loading={loading} />
    </div>
  );
};

export default BacktestPage;