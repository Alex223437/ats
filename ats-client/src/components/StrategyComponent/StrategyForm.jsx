import { useState, useEffect } from 'react';
import './StrategyForm.scss';
import { fetchUserStocks } from '../../services/stockService';
import { fetchStrategyTickers, setStrategyTickers } from '../../services/strategyService';
import { toast } from 'react-hot-toast';

const availableIndicators = ['RSI', 'MACD', 'SMA', 'Bollinger Bands'];

const StrategyForm = ({ strategy, onSave, onDelete }) => {
  const [title, setTitle] = useState('');
  const [buySignals, setBuySignals] = useState([]);
  const [sellSignals, setSellSignals] = useState([]);
  const [marketCheckFrequency, setMarketCheckFrequency] = useState('1 Hour');
  const [automationMode, setAutomationMode] = useState('Semi-Automatic');
  const [availableTickers, setAvailableTickers] = useState([]);
  const [selectedTickers, setSelectedTickers] = useState([]);
  const [signalLogic, setSignalLogic] = useState('AND');
  const [confirmationCandles, setConfirmationCandles] = useState(1);
  const [notifyOnSignal, setNotifyOnSignal] = useState(true);
  const [autoTrade, setAutoTrade] = useState(false);
  const [orderType, setOrderType] = useState('market');
  const [tradeAmount, setTradeAmount] = useState(100);
  const isEditable = !strategy?.is_enabled;

  useEffect(() => {
    const init = async () => {
      const userTickers = await fetchUserStocks();
      setAvailableTickers(userTickers);

      if (strategy) {
        setTitle(strategy.title);
        setBuySignals(strategy.buy_signals || []);
        setSellSignals(strategy.sell_signals || []);
        setMarketCheckFrequency(strategy.market_check_frequency);
        setAutomationMode(strategy.automation_mode);
        setSignalLogic(strategy.signal_logic || 'AND');
        setConfirmationCandles(strategy.confirmation_candles || 1);
        setNotifyOnSignal(strategy.notify_on_signal ?? true);
        setAutoTrade(strategy.auto_trade ?? false);
        setOrderType(strategy.order_type || 'market');
        setTradeAmount(strategy.trade_amount || 100);

        const strategyTickers = await fetchStrategyTickers(strategy.id);
        setSelectedTickers(strategyTickers);
      } else {
        setTitle('');
        setBuySignals([]);
        setSellSignals([]);
        setMarketCheckFrequency('1 Hour');
        setAutomationMode('Semi-Automatic');
        setSelectedTickers([]);
      }
    };

    init();
  }, [strategy]);

  const handleSignalChange = (type, index, value) => {
    const newSignals = [...(type === 'buy' ? buySignals : sellSignals)];
    newSignals[index].value = Number(value);
    type === 'buy' ? setBuySignals(newSignals) : setSellSignals(newSignals);
  };

  const handleAddSignal = (type) => {
    const newSignal = { indicator: 'RSI', value: 50 };
    type === 'buy'
      ? setBuySignals([...buySignals, newSignal])
      : setSellSignals([...sellSignals, newSignal]);
  };

  const handleSubmit = async () => {
  if (!title.trim()) {
    toast.error('Strategy title is required');
    return;
  }

  if (buySignals.length === 0 && sellSignals.length === 0) {
    toast.error('Add at least one buy or sell signal');
    return;
  }

  try {
    const saved = await onSave({
      title,
      buy_signals: buySignals,
      sell_signals: sellSignals,
      market_check_frequency: marketCheckFrequency,
      automation_mode: automationMode,
      signal_logic: signalLogic,
      confirmation_candles: confirmationCandles,
      notify_on_signal: notifyOnSignal,
      auto_trade: autoTrade,
      order_type: orderType,
      trade_amount: tradeAmount,
    });

    if (saved?.id && selectedTickers.length) {
      await setStrategyTickers(saved.id, selectedTickers);
    }

    toast.success('Strategy saved successfully!');
  } catch (err) {
    toast.error('Failed to save strategy');
  }
};

  return (
    <div className="strategy-form">
      <h2>Strategy Settings</h2>

      {strategy?.is_enabled && (
        <p className="form-warning">
          This strategy is currently running. Stop it before making changes.
        </p>
      )}

      <label>Title</label>
      <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} disabled={!isEditable}/>

      <h3>Buy Signals</h3>
      {buySignals.map((signal, index) => (
        <div key={index} className="signal-container">
          <select
            disabled={!isEditable}
            value={signal.indicator}
            onChange={(e) => {
              const newSignals = [...buySignals];
              newSignals[index].indicator = e.target.value;
              setBuySignals(newSignals);
            }}
          >
            {availableIndicators.map((ind) => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>
          <input
            disabled={!isEditable}
            type="number"
            min="0"
            max="100"
            value={signal.value}
            onChange={(e) => handleSignalChange('buy', index, e.target.value)}
          />
        </div>
      ))}
      <button onClick={() => handleAddSignal('buy')} disabled={!isEditable}>+ Add Buy Signal</button>

      <h3>Sell Signals</h3>
      {sellSignals.map((signal, index) => (
        <div key={index} className="signal-container">
          <select
            disabled={!isEditable}
            value={signal.indicator}
            onChange={(e) => {
              const newSignals = [...sellSignals];
              newSignals[index].indicator = e.target.value;
              setSellSignals(newSignals);
            }}
          >
            {availableIndicators.map((ind) => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>
          <input
            disabled={!isEditable}
            type="number"
            min="0"
            max="100"
            value={signal.value}
            onChange={(e) => handleSignalChange('sell', index, e.target.value)}
          />
        </div>
      ))}
      <button onClick={() => handleAddSignal('sell')} disabled={!isEditable}>+ Add Sell Signal</button>

      <div className="input-group-row">
        <div>
           <label>Market Check Frequency</label>
            <select
              disabled={!isEditable}
              value={marketCheckFrequency}
              onChange={(e) => setMarketCheckFrequency(e.target.value)}
            >
              <option>1 Minute</option>
              <option>5 Minutes</option>
              <option>15 Minutes</option>
              <option>1 Hour</option>
              <option>1 Day</option>
            </select>
        </div>
        <div>
          <label>Automation Mode</label>
      <select
        disabled={!isEditable}
        value={automationMode}
        onChange={(e) => setAutomationMode(e.target.value)}
      >
        <option>Semi-Automatic</option>
        <option>Automatic</option>
        <option>Manual</option>
      </select>
        </div>
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

      <h3>Execution Settings</h3>

      <div className="input-group-row">
        <div>
          <label>Signal Logic</label>
          <select value={signalLogic} onChange={(e) => setSignalLogic(e.target.value)} disabled={!isEditable}>
            <option value="AND">AND</option>
            <option value="OR">OR</option>
          </select>
        </div>
        <div>
          <label>Confirmation Candles</label>
          <input
            disabled={!isEditable}
            type="number"
            min="1"
            value={confirmationCandles}
            onChange={(e) => setConfirmationCandles(Number(e.target.value))}
          />
        </div>
      </div>

      <label>
        <input
          disabled={!isEditable}
          type="checkbox"
          checked={notifyOnSignal}
          onChange={(e) => setNotifyOnSignal(e.target.checked)}
        />
        Notify on Signal
      </label>

      <label>
        <input
          disabled={!isEditable}
          type="checkbox"
          checked={autoTrade}
          onChange={(e) => setAutoTrade(e.target.checked)}
        />
        Enable Auto-Trade
      </label>

      <div className="input-group-row">
        <div>
          <label>Order Type</label>
          <select value={orderType} onChange={(e) => setOrderType(e.target.value)} disabled={!isEditable}>
            <option value="market">Market</option>
            <option value="limit">Limit</option>
            <option value="stop">Stop</option>
            <option value="trailing_stop">Trailing Stop</option>
          </select>
        </div>
        <div>
          <label>Trade Amount ($)</label>
          <input
            disabled={!isEditable}
            type="number"
            min="1"
            value={tradeAmount}
            onChange={(e) => setTradeAmount(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="button-group">
        <button onClick={handleSubmit} disabled={!isEditable}>Save</button>
        {strategy && <button disabled={!isEditable} className="delete" onClick={() => onDelete(strategy.id)}>Delete</button>}
      </div>
    </div>
  );
};

export default StrategyForm;
