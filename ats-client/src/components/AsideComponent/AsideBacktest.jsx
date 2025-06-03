import React, { useState } from 'react';
import AsideLayout from './AsideLayout';
import useStrategiesAndTickers from '@/hooks/useStrategiesAndTickers';

const AsideBacktest = ({ onRun }) => {
  const [strategyId, setStrategyId] = useState('');
  const [ticker, setTicker] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { strategies, tickers } = useStrategiesAndTickers();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!strategyId || !ticker || !startDate || !endDate) return;

    onRun?.({
      strategy_id: parseInt(strategyId),
      ticker,
      parameters: {}, 
      start_date: startDate,
      end_date: endDate,
    });
  };

  return (
    <AsideLayout title="Backtest">
      <form className="aside__form" onSubmit={handleSubmit}>
        <select value={strategyId} onChange={(e) => setStrategyId(e.target.value)} required>
          <option value="">Select Strategy</option>
          {strategies.map((s) => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>

        <select value={ticker} onChange={(e) => setTicker(e.target.value)} required>
          <option value="">Select Ticker</option>
          {tickers.stocks?.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />

        <button type="submit" className="aside__form__submit">Run Backtest</button>
      </form>
    </AsideLayout>
  );
};

export default AsideBacktest;