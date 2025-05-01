import { useState, useEffect } from 'react';
import './StrategyForm.scss';

const availableIndicators = ['RSI', 'MACD', 'SMA', 'Bollinger Bands'];

const StrategyForm = ({ strategy, onSave, onDelete }) => {
  const [title, setTitle] = useState('');
  const [buySignals, setBuySignals] = useState([]);
  const [sellSignals, setSellSignals] = useState([]);
  const [marketCheckFrequency, setMarketCheckFrequency] = useState('1 Hour');
  const [automationMode, setAutomationMode] = useState('Semi-Automatic');

  useEffect(() => {
    if (strategy) {
      setTitle(strategy.title);
      setBuySignals(strategy.buy_signals || []);
      setSellSignals(strategy.sell_signals || []);
      setMarketCheckFrequency(strategy.market_check_frequency);
      setAutomationMode(strategy.automation_mode);
    } else {
      // Очищаем поля при создании новой стратегии
      setTitle('');
      setBuySignals([]);
      setSellSignals([]);
      setMarketCheckFrequency('1 Hour');
      setAutomationMode('Semi-Automatic');
    }
  }, [strategy]);

  const handleSignalChange = (type, index, value) => {
    const newSignals = [...(type === 'buy' ? buySignals : sellSignals)];
    newSignals[index].value = Number(value); // 🔥 Преобразуем в число
    type === 'buy' ? setBuySignals(newSignals) : setSellSignals(newSignals);
  };

  const handleAddSignal = (type) => {
    const newSignal = { indicator: 'RSI', value: 50 };
    type === 'buy'
      ? setBuySignals([...buySignals, newSignal])
      : setSellSignals([...sellSignals, newSignal]);
  };

  const handleSubmit = () => {
    onSave({
      title,
      buy_signals: buySignals,
      sell_signals: sellSignals,
      market_check_frequency: marketCheckFrequency,
      automation_mode: automationMode,
    });
  };

  return (
    <div className="strategy-form">
      <h2>Strategy Settings</h2>
      <label>Title</label>
      <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />

      <h3>Buy Signals</h3>
      {buySignals.map((signal, index) => (
        <div key={index}>
          <select
            value={signal.indicator}
            onChange={(e) => {
              const newSignals = [...buySignals];
              newSignals[index].indicator = e.target.value;
              setBuySignals(newSignals);
            }}
          >
            {availableIndicators.map((ind) => (
              <option key={ind} value={ind}>
                {ind}
              </option>
            ))}
          </select>
          <input
            type="range"
            min="0"
            max="100"
            value={signal.value}
            onChange={(e) => handleSignalChange('buy', index, e.target.value)}
          />
          <span>{signal.value}</span>
        </div>
      ))}
      <button onClick={() => handleAddSignal('buy')}>+ Add Buy Signal</button>

      <h3>Sell Signals</h3>
      {sellSignals.map((signal, index) => (
        <div key={index}>
          <select
            value={signal.indicator}
            onChange={(e) => {
              const newSignals = [...sellSignals];
              newSignals[index].indicator = e.target.value;
              setSellSignals(newSignals);
            }}
          >
            {availableIndicators.map((ind) => (
              <option key={ind} value={ind}>
                {ind}
              </option>
            ))}
          </select>
          <input
            type="range"
            min="0"
            max="100"
            value={signal.value}
            onChange={(e) => handleSignalChange('sell', index, e.target.value)}
          />
          <span>{signal.value}</span>
        </div>
      ))}
      <button onClick={() => handleAddSignal('sell')}>+ Add Sell Signal</button>

      <label>Market Check Frequency</label>
      <select
        value={marketCheckFrequency}
        onChange={(e) => setMarketCheckFrequency(e.target.value)}
      >
        <option>1 Minute</option>
        <option>5 Minutes</option>
        <option>15 Minutes</option>
        <option>1 Hour</option>
        <option>1 Day</option>
      </select>

      <label>Automation Mode</label>
      <select value={automationMode} onChange={(e) => setAutomationMode(e.target.value)}>
        <option>Semi-Automatic</option>
        <option>Automatic</option>
        <option>Manual</option>
      </select>

      <button onClick={handleSubmit}>Save</button>
      {strategy && <button onClick={() => onDelete(strategy.id)}>Delete</button>}
    </div>
  );
};

export default StrategyForm;
