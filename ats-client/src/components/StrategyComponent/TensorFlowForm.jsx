import { useState, useEffect } from 'react';
import { fetchUserStocks } from '../../services/stockService';
import { toast } from 'react-hot-toast';
import StarIcon from '@/assets/svg/star1.svg?react';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import { fetchStrategyTickers, setStrategyTickers } from '../../services/strategyService';

const TensorFlowStrategyForm = ({ strategy, onSave, onTrain, onDeleteModel }) => {
  const [title, setTitle] = useState('');
  const [availableTickers, setAvailableTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState('');
  const [selectedTickers, setSelectedTickers] = useState([]);
  const [fromDate, setFromDate] = useState('2024-01-01');
  const [toDate, setToDate] = useState('2025-03-01');
  const [isTraining, setIsTraining] = useState(false);
  const [tradeAmount, setTradeAmount] = useState(1);
  const [useNotional, setUseNotional] = useState(false);
  const [useBalancePercent, setUseBalancePercent] = useState(false);
  const [automationMode, setAutomationMode] = useState('NotifyOnly');

  const isEditable = !strategy?.is_enabled;

  useEffect(() => {
    const init = async () => {
      const tickers = await fetchUserStocks();
      setAvailableTickers(tickers);

      if (strategy) {
        setTitle(strategy.title || '');
        setSelectedTicker(strategy.training_ticker || '');
        setFromDate(strategy.training_from_date || '2024-01-01');
        setToDate(strategy.training_to_date || '2025-03-01');
        setAutomationMode(strategy.automation_mode || 'NotifyOnly');
        setTradeAmount(strategy.trade_amount || 1);
        setUseNotional(strategy.use_notional ?? false);
        setUseBalancePercent(strategy.use_balance_percent ?? false);

        const tickersLinked = await fetchStrategyTickers(strategy.id);
        setSelectedTickers(tickersLinked);
      }
    };
    init();
  }, [strategy]);

  const handleToggleNotional = (checked) => {
    if (checked && useBalancePercent) {
      toast.error('Cannot enable both Notional and Balance Percent.');
      return;
    }
    setUseNotional(checked);
  };

  const handleToggleBalancePercent = (checked) => {
    if (checked && useNotional) {
      toast.error('Cannot enable both Balance Percent and Notional.');
      return;
    }
    setUseBalancePercent(checked);
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      toast.error('Strategy title is required');
      return;
    }
    if (!selectedTicker) {
      toast.error('Please select a ticker');
      return;
    }

    try {
      const saved = await onSave({
        title,
        training_ticker: selectedTicker,
        training_from_date: fromDate,
        training_to_date: toDate,
        automation_mode: automationMode,
        trade_amount: tradeAmount,
        use_notional: useNotional,
        use_balance_percent: useBalancePercent,
        strategy_type: "ml_tf"
      });

      if (saved?.id && selectedTickers.length) {
        await setStrategyTickers(saved.id, selectedTickers);
      }

      toast.success('TensorFlow strategy saved successfully!');
    } catch (err) {
      toast.error('Failed to save strategy');
    }
  };

  const handleTrain = async () => {
    try {
      setIsTraining(true);
      await onTrain(strategy.id);
      toast.success('Model trained successfully!');
    } catch (err) {
      toast.error('Training failed');
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="strategy-form">
      <h2>TensorFlow Strategy Settings</h2>
      {strategy?.is_enabled && (
        <p className="form-warning">
          This strategy is currently running. Stop it before making changes.
        </p>
      )}

      {strategy?.last_trained_at && (
        <div className="model-status-card">
          <div className="model-header">
            <h3>Model Status</h3>
            <span className="model-tag">Trained</span>
          </div>
          <div className="model-info">
            Last trained: {new Date(strategy.last_trained_at).toLocaleString()}
          </div>
          <div className="model-actions">
            <button onClick={() => onDeleteModel(strategy.id)}>Delete Model</button>
          </div>
        </div>
      )}

      <label>Title</label>
      <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} disabled={!isEditable} />

      <label>Training Ticker</label>
      <select
        value={selectedTicker}
        onChange={(e) => setSelectedTicker(e.target.value)}
        disabled={!isEditable}
      >
        <option value="">Select Ticker</option>
        {availableTickers.map((ticker) => (
          <option key={ticker} value={ticker}>{ticker}</option>
        ))}
      </select>

      <label>Training Date Range</label>
      <div className="input-group-row">
        <div>
          <label>From Date</label>
          <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} disabled={!isEditable} />
        </div>
        <div>
          <label>To Date</label>
          <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} disabled={!isEditable} />
        </div>
      </div>

      <label>Automation Mode</label>
      <select
        value={automationMode}
        onChange={(e) => setAutomationMode(e.target.value)}
        disabled={!isEditable}
      >
        {['Manual', 'NotifyOnly', 'SemiAuto', 'FullAuto'].map((mode) => (
          <option key={mode} value={mode}>{mode}</option>
        ))}
      </select>

      <label>Trade Amount</label>
      <input
        type="number"
        value={tradeAmount}
        onChange={(e) => setTradeAmount(Number(e.target.value))}
        disabled={!isEditable}
      />

      <div className="checkbox-row">
        <label className="custom-checkbox">
          <input
            type="checkbox"
            checked={useNotional}
            onChange={(e) => handleToggleNotional(e.target.checked)}
            disabled={!isEditable}
          />
          <span className="checkmark" />
          Use Notional
        </label>

        <label className="custom-checkbox">
          <input
            type="checkbox"
            checked={useBalancePercent}
            onChange={(e) => handleToggleBalancePercent(e.target.checked)}
            disabled={!isEditable}
          />
          <span className="checkmark" />
          Use % of Balance
        </label>
      </div>

      <label>Apply to Tickers</label>
      <div className="ticker-checkboxes">
        {availableTickers.map((ticker) => (
          <label key={ticker}>
            <input
              disabled={!isEditable}
              type="checkbox"
              checked={selectedTickers.includes(ticker)}
              onChange={() => {
                if (selectedTickers.includes(ticker)) {
                  setSelectedTickers(selectedTickers.filter(t => t !== ticker));
                } else {
                  setSelectedTickers([...selectedTickers, ticker]);
                }
              }}
            />
            {ticker}
          </label>
        ))}
      </div>

      <div className="button-group">
        <button onClick={handleSubmit} disabled={!isEditable}>Save</button>
        {isTraining && <LoaderSpinner className="loading-spinner" />}
        {strategy && (
          <button onClick={handleTrain} disabled={!isEditable || isTraining} className="train-button">
            {isTraining ? 'Training...' : 'Train'}
          </button>
        )}
      </div>

      <StarIcon className="tensorflow-icon" />
    </div>
  );
};

export default TensorFlowStrategyForm;