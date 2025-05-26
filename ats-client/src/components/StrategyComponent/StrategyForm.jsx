import { useState, useEffect } from 'react';
import './StrategyForm.scss';
import { fetchUserStocks } from '../../services/stockService';
import { fetchStrategyTickers, setStrategyTickers } from '../../services/strategyService';
import { fetchTradingPreferences } from '../../services/tradeService';
import { toast } from 'react-hot-toast';

const availableIndicators = ['RSI', 'MACD', 'SMA', 'Bollinger Bands'];
const availableTimeframes = ['1Min', '5Min', '1H', '1D'];
const automationModes = ['Manual', 'NotifyOnly', 'SemiAuto', 'FullAuto'];
const availableOperators = ['<', '<=', '==', '>=', '>'];


const StrategyForm = ({ strategy, onSave, onDelete }) => {
  const [title, setTitle] = useState('');
  const [buySignals, setBuySignals] = useState([]);
  const [sellSignals, setSellSignals] = useState([]);
  const [marketCheckFrequency, setMarketCheckFrequency] = useState('1 Hour');
  const [automationMode, setAutomationMode] = useState('SemiAuto');
  const [availableTickers, setAvailableTickers] = useState([]);
  const [selectedTickers, setSelectedTickers] = useState([]);
  const [signalLogic, setSignalLogic] = useState('AND');
  const [confirmationCandles, setConfirmationCandles] = useState(1);
  const [orderType, setOrderType] = useState('market');
  const [tradeAmount, setTradeAmount] = useState(100);
  const [useNotional, setUseNotional] = useState(false);
  const [useBalancePercent, setUseBalancePercent] = useState(false);
  const [stopLoss, setStopLoss] = useState();
  const [takeProfit, setTakeProfit] = useState();
  const [slTpIsPercent, setSlTpIsPercent] = useState(true);
  const [defaultTimeframe, setDefaultTimeframe] = useState('1H');
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
        setOrderType(strategy.order_type || 'market');
        setTradeAmount(strategy.trade_amount || 100);
        setUseNotional(strategy.use_notional ?? false);
        setUseBalancePercent(strategy.use_balance_percent ?? false);
        setStopLoss(strategy.stop_loss ?? undefined);
        setTakeProfit(strategy.take_profit ?? undefined);
        setSlTpIsPercent(strategy.sl_tp_is_percent ?? true);
        setDefaultTimeframe(strategy.default_timeframe || '1H');

        const strategyTickers = await fetchStrategyTickers(strategy.id);
        setSelectedTickers(strategyTickers);
      } else {
        try {
          const preferences = await fetchTradingPreferences();
          setTitle('');
          setBuySignals([]);
          setSellSignals([]);
          setMarketCheckFrequency('1 Hour');
          setAutomationMode(preferences.auto_trading_enabled ? 'FullAuto' : 'NotifyOnly');
          setSelectedTickers([]);
          setTradeAmount(preferences.default_trade_amount);
          setUseBalancePercent(preferences.use_percentage);
          setUseNotional(!preferences.use_percentage);
          setStopLoss(preferences.default_stop_loss ?? undefined);
          setTakeProfit(preferences.default_take_profit ?? undefined);
          setDefaultTimeframe(preferences.default_timeframe);
        } catch (err) {
          toast.error('Failed to load preferences');
        }
      }
    };

    init();
  }, [strategy]);

  const handleSignalChange = (type, index, field, value) => {
    const newSignals = [...(type === 'buy' ? buySignals : sellSignals)];
    newSignals[index][field] = field === 'value' ? Number(value) : value;
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

    let sl = stopLoss;
    let tp = takeProfit;

    if (useNotional || useBalancePercent) {
      sl = null;
      tp = null;
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
        order_type: orderType,
        trade_amount: tradeAmount,
        use_notional: useNotional,
        use_balance_percent: useBalancePercent,
        stop_loss: sl,
        take_profit: tp,
        sl_tp_is_percent: slTpIsPercent,
        default_timeframe: defaultTimeframe
      });

      if (saved?.id && selectedTickers.length) {
        await setStrategyTickers(saved.id, selectedTickers);
      }

      toast.success('Strategy saved successfully!');
    } catch (err) {
      toast.error('Failed to save strategy');
    }
  };
  const renderSignalRow = (signal, index, type) => (
    <div key={index} className="signal-container">
      <select
        disabled={!isEditable}
        value={signal.indicator}
        onChange={(e) => handleSignalChange(type, index, 'indicator', e.target.value)}
      >
        {availableIndicators.map((ind) => (
          <option key={ind} value={ind}>{ind}</option>
        ))}
      </select>
      <select
        disabled={!isEditable}
        value={signal.operator || '>'}
        onChange={(e) => handleSignalChange(type, index, 'operator', e.target.value)}
      >
        {availableOperators.map(op => (
          <option key={op} value={op}>{op}</option>
        ))}
      </select>
      <input
        disabled={!isEditable}
        type="number"
        min="0"
        max="100"
        value={signal.value}
        onChange={(e) => handleSignalChange(type, index, 'value', e.target.value)}
      />
    </div>
  );

  const handleToggleNotional = (checked) => {
    setUseNotional(checked);
    if (checked) setUseBalancePercent(false);
    if (checked) {
      setStopLoss(undefined);
      setTakeProfit(undefined);
    }
  };

  const handleToggleBalancePercent = (checked) => {
    setUseBalancePercent(checked);
    if (checked) setUseNotional(false);
    if (checked) {
      setStopLoss(undefined);
      setTakeProfit(undefined);
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
      {buySignals.map((signal, index) => renderSignalRow(signal, index, 'buy'))}
      <button onClick={() => handleAddSignal('buy')} disabled={!isEditable}>+ Add Buy Signal</button>

      <h3>Sell Signals</h3>
      {sellSignals.map((signal, index) => renderSignalRow(signal, index, 'sell'))}
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
          <select disabled={!isEditable} value={automationMode} onChange={(e) => setAutomationMode(e.target.value)}>
            {automationModes.map(mode => <option key={mode} value={mode}>{mode}</option>)}
          </select>
        </div>
        <div>
          <label>Timeframe</label>
          <select disabled={!isEditable} value={defaultTimeframe} onChange={(e) => setDefaultTimeframe(e.target.value)}>
            {availableTimeframes.map(tf => <option key={tf}>{tf}</option>)}
          </select>
        </div>
      </div>
     

      {/* <label>Use Notional ($)</label>
      <input
        type="checkbox"
        disabled={!isEditable}
        checked={useNotional}
        onChange={(e) => setUseNotional(e.target.checked)}
      /> */}

      {/* <label>Use % of Balance</label>
      <input
        type="checkbox"
        disabled={!isEditable}
        checked={useBalancePercent}
        onChange={(e) => setUseBalancePercent(e.target.checked)}
      /> */}

      <label>Trade Amount (Default - quantity)</label>
      <input
        type="number"
        disabled={!isEditable}
        value={tradeAmount}
        onChange={(e) => setTradeAmount(Number(e.target.value))}
      />

      <div className="checkbox-row">
        <label className="custom-checkbox">
          <input
            type="checkbox"
            disabled={!isEditable}
            checked={useNotional}
            onChange={(e) => handleToggleNotional(e.target.checked)}
          />
          <span className="checkmark" />
          Use Notional ($)
        </label>

        <label className="custom-checkbox">
          <input
            type="checkbox"
            disabled={!isEditable}
            checked={useBalancePercent}
            onChange={(e) => handleToggleBalancePercent(e.target.checked)}
          />
          <span className="checkmark" />
          Use % of Balance
        </label>

        <label className="custom-checkbox">
          <input
            type="checkbox"
            disabled={!isEditable}
            checked={slTpIsPercent}
            onChange={(e) => setSlTpIsPercent(e.target.checked)}
          />
          <span className="checkmark" />
          SL/TP in Percent
        </label>
      </div>

      <div className="input-group-row">
        <div>
          <label>Stop Loss</label>
          <input
            type="number"
            disabled={!isEditable || useNotional || useBalancePercent}
            value={stopLoss ?? ''}
            onChange={(e) => setStopLoss(Number(e.target.value))}
            placeholder="Optional (works with qty only)"
          />
        </div>
        <div>
          <label>Take Profit</label>
          <input
            type="number"
            disabled={!isEditable || useNotional || useBalancePercent}
            value={takeProfit ?? ''}
            onChange={(e) => setTakeProfit(Number(e.target.value))}
            placeholder="Optional (works with qty only)"
          />
        </div>
      </div>

      {/* <label>SL/TP in Percent</label>
      <input
        type="checkbox"
        disabled={!isEditable}
        checked={slTpIsPercent}
        onChange={(e) => setSlTpIsPercent(e.target.checked)}
      /> */}

      

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
      </div>

      <div className="button-group">
        <button onClick={handleSubmit} disabled={!isEditable}>Save</button>
        {strategy && <button disabled={!isEditable} className="delete" onClick={() => onDelete(strategy.id)}>Delete</button>}
      </div>
    </div>
  );
};

export default StrategyForm;
