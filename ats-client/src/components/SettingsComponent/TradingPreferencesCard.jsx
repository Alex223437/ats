import { useEffect, useState } from 'react';
import useSettingsApi from '@/hooks/useSettingsApi';
import toast from 'react-hot-toast';

const timeframes = ['1Min', '5Min', '1H', '1D'];

const TradingPreferencesCard = () => {
  const {
    fetchTradingPreferences,
    updateTradingPreferences,
    tradingPreferences,
    loadingTradingPrefs,
    updatingTradingPrefs,
  } = useSettingsApi();

  const [timeframe, setTimeframe] = useState('1Min');
  const [autoTrading, setAutoTrading] = useState(false);
  const [tradeAmount, setTradeAmount] = useState('100');
  const [usePercent, setUsePercent] = useState(false);
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');

  useEffect(() => {
    fetchTradingPreferences();
  }, []);

  useEffect(() => {
    if (tradingPreferences) {
      setTimeframe(tradingPreferences.default_timeframe);
      setAutoTrading(tradingPreferences.auto_trading_enabled);
      setTradeAmount(String(tradingPreferences.default_trade_amount));
      setUsePercent(tradingPreferences.use_percentage);
      setStopLoss(tradingPreferences.default_stop_loss || '');
      setTakeProfit(tradingPreferences.default_take_profit || '');
    }
  }, [tradingPreferences]);

  const handleSave = async () => {
    try {
      await updateTradingPreferences({
        default_timeframe: timeframe,
        auto_trading_enabled: autoTrading,
        default_trade_amount: parseFloat(tradeAmount),
        use_percentage: usePercent,
        default_stop_loss: stopLoss ? parseFloat(stopLoss) : null,
        default_take_profit: takeProfit ? parseFloat(takeProfit) : null,
      });
      toast.success('Trading preferences saved');
    } catch {
      toast.error('Failed to save preferences');
    }
  };

  return (
    <div className="settings-form trading-preferences">
      <h2>Trading Preferences</h2>

      <label>Default Timeframe</label>
      <div className="toggle-group">
        {timeframes.map((tf) => (
          <button
            key={tf}
            type="button"
            className={timeframe === tf ? 'active' : ''}
            onClick={() => setTimeframe(tf)}
          >
            {tf}
          </button>
        ))}
      </div>

      <label>Auto-Trading</label>
      <div className="toggle-group">
        <button
          type="button"
          className={autoTrading ? 'active' : ''}
          onClick={() => setAutoTrading(true)}
        >
          On
        </button>
        <button
          type="button"
          className={!autoTrading ? 'active' : ''}
          onClick={() => setAutoTrading(false)}
        >
          Off
        </button>
      </div>

      <label>Default Trade Amount</label>
      <div className="inline-input-group">
        <input
          type="text"
          value={tradeAmount}
          onChange={(e) => setTradeAmount(e.target.value)}
        />
        <div className="toggle-group">
          <button
            type="button"
            className={!usePercent ? 'active' : ''}
            onClick={() => setUsePercent(false)}
          >
            $
          </button>
          <button
            type="button"
            className={usePercent ? 'active' : ''}
            onClick={() => setUsePercent(true)}
          >
            %
          </button>
        </div>
      </div>

      <div className="input-group-row">
        <div>
          <label>Default Stop-Loss</label>
          <input
            type="text"
            value={stopLoss}
            onChange={(e) => setStopLoss(e.target.value)}
          />
        </div>
        <div>
          <label>Default Take-Profit</label>
          <input
            type="text"
            value={takeProfit}
            onChange={(e) => setTakeProfit(e.target.value)}
          />
        </div>
      </div>

      <div className="button-group">
        <button onClick={handleSave} disabled={updatingTradingPrefs}>
          {updatingTradingPrefs ? 'Saving...' : 'Save'}
        </button>
      </div>
    </div>
  );
};

export default TradingPreferencesCard;