import React, { useState } from 'react';
import AsideLayout from './AsideLayout';
import useStrategiesAndTickers from '@/hooks/useStrategiesAndTickers';

const AsideFiltersAnalytics = ({ onApply }) => {
  const [strategyId, setStrategyId] = useState('');
  const [ticker, setTicker] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { strategies, tickers } = useStrategiesAndTickers();

  const handleSubmit = (e) => {
    e.preventDefault();
    onApply?.({
      strategyId: strategyId || undefined,
      ticker: ticker || undefined,
      startDate: startDate || undefined,
      endDate: endDate || undefined,
    });
  };

  return (
    <AsideLayout title="Filters">
      <form className="aside__form" onSubmit={handleSubmit}>
        <select value={strategyId} onChange={(e) => setStrategyId(e.target.value)}>
          <option value="">All Strategies</option>
          {strategies.map((s) => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>

        <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
          <option value="">All Tickers</option>
          {tickers.stocks?.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        <button type="submit" className="aside__form__submit">Apply</button>
      </form>
    </AsideLayout>
  );
};

export default AsideFiltersAnalytics;