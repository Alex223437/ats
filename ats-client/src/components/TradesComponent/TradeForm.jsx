import { useState } from 'react';
import { placeOrder } from '@/services/tradeService';
import allTickers from '@/data/tickers.json';
import toast from 'react-hot-toast';
import './TradeForm.scss';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';

const TradeForm = ({ onOrderPlaced }) => {
  const [side, setSide] = useState('buy');
  const [symbol, setSymbol] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [orderType, setOrderType] = useState('market');
  const [qty, setQty] = useState(1);
  const [notional, setNotional] = useState('');
  const [timeInForce, setTimeInForce] = useState('day');
  const [limitPrice, setLimitPrice] = useState('');
  const [stopPrice, setStopPrice] = useState('');
  const [trailPrice, setTrailPrice] = useState('');
  const [trailPercent, setTrailPercent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setSymbol(value);
    if (value.length >= 2) {
      const matches = allTickers.filter((t) => t.ticker.startsWith(value)).slice(0, 10);
      setSuggestions(matches);
    } else {
      setSuggestions([]);
    }
  };

  const selectSuggestion = (ticker) => {
    setSymbol(ticker);
    setSuggestions([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = symbol.trim().toUpperCase();

    if (!trimmed) return toast.error('Please enter a ticker symbol');
    if (!allTickers.some((t) => t.ticker === trimmed)) {
      return toast.error(`Ticker "${trimmed}" not found`);
    }

    const order = {
      symbol: trimmed,
      side,
      order_type: orderType,
      time_in_force: timeInForce,
    };

    if (notional) {
      order.notional = parseFloat(notional);
    } else {
      order.qty = Number(qty);
    }

    if (notional && qty) {
      return toast.error("You can't specify both quantity and notional");
    }

    if (orderType === 'limit') order.limit_price = parseFloat(limitPrice);
    if (orderType === 'stop') order.stop_price = parseFloat(stopPrice);
    if (orderType === 'stop_limit') {
      order.stop_price = parseFloat(stopPrice);
      order.limit_price = parseFloat(limitPrice);
    }
    if (orderType === 'trailing_stop') {
      if (trailPrice) order.trail_price = parseFloat(trailPrice);
      if (trailPercent) order.trail_percent = parseFloat(trailPercent);
    }

    try {
      setLoading(true);
      await placeOrder(order);
      toast.success('Order placed successfully!');
      setSymbol('');
      setLimitPrice('');
      setStopPrice('');
      setTrailPrice('');
      setTrailPercent('');
      setQty(1);
      setNotional('');
      onOrderPlaced?.();
    } catch {
      toast.error('Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="trade-form" onSubmit={handleSubmit}>
      <h2>Create Order</h2>

      <div className="side-selector">
        <button type="button" onClick={() => setSide('buy')} className={side === 'buy' ? 'active-buy' : ''}>Buy</button>
        <button type="button" onClick={() => setSide('sell')} className={side === 'sell' ? 'active-sell' : ''}>Sell</button>
      </div>

      <label htmlFor="symbol">Ticker Symbol</label>
      <input
        id="symbol"
        type="text"
        value={symbol}
        onChange={handleInputChange}
        onBlur={() => setTimeout(() => setSuggestions([]), 100)}
        onFocus={(e) => handleInputChange({ target: { value: symbol } })}
        placeholder="e.g. AAPL"
        autoComplete="off"
      />
      {suggestions.length > 0 && (
        <ul className="suggestions-list">
          {suggestions.map((s) => (
            <li key={s.ticker} onMouseDown={() => selectSuggestion(s.ticker)}>
              <strong>{s.ticker}</strong> — {s.name}
            </li>
          ))}
        </ul>
      )}

      <label htmlFor="orderType">Order Type</label>
      <select id="orderType" value={orderType} onChange={(e) => setOrderType(e.target.value)}>
        <option value="market">Market</option>
        <option value="limit">Limit</option>
        <option value="stop">Stop</option>
        <option value="stop_limit">Stop Limit</option>
        <option value="trailing_stop">Trailing Stop</option>
      </select>

      {(orderType === 'limit' || orderType === 'stop_limit') && (
        <>
          <label htmlFor="limitPrice">Limit Price</label>
          <input type="number" id="limitPrice" value={limitPrice} onChange={(e) => setLimitPrice(e.target.value)} />
        </>
      )}

      {(orderType === 'stop' || orderType === 'stop_limit') && (
        <>
          <label htmlFor="stopPrice">Stop Price</label>
          <input type="number" id="stopPrice" value={stopPrice} onChange={(e) => setStopPrice(e.target.value)} />
        </>
      )}

      {orderType === 'trailing_stop' && (
        <>
          <label htmlFor="trailPrice">Trail Price</label>
          <input type="number" id="trailPrice" value={trailPrice} onChange={(e) => setTrailPrice(e.target.value)} />
          <label htmlFor="trailPercent">Trail Percent</label>
          <input type="number" id="trailPercent" value={trailPercent} onChange={(e) => setTrailPercent(e.target.value)} />
        </>
      )}

      <label htmlFor="qty">Quantity</label>
      <input type="number" id="qty" value={qty} onChange={(e) => setQty(e.target.value)} disabled={!!notional} />

      <label htmlFor="notional">Notional ($)</label>
      <input 
        type="number"
        id="notional"
        value={notional}
        onChange={(e) => setNotional(e.target.value)}
        disabled={qty || orderType !== 'market' || timeInForce !=="day"} />

      <label htmlFor="timeInForce">Time in Force</label>
      <select id="timeInForce" value={timeInForce} onChange={(e) => setTimeInForce(e.target.value)}>
        <option value="day">DAY</option>
        <option value="gtc">GTC</option>
      </select>

      <button className="submit-btn" type="submit" disabled={loading}>
        {loading ? (
          <div className="spinner-wrapper">
            <LoaderSpinner size={18} />
            Submitting...
          </div>
        ) : (
          'Place Order'
        )}
      </button>
    </form>
  );
};

export default TradeForm;