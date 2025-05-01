import { useState, useRef } from 'react';
import { placeOrder } from '../../services/tradeService';
import './CreateOrderModal.scss';

const OrderModal = ({ onClose, isOpen }) => {
  const [side, setSide] = useState('buy');
  const [symbol, setSymbol] = useState('');
  const [orderType, setOrderType] = useState('market');
  const [qty, setQty] = useState(1);
  const [timeInForce, setTimeInForce] = useState('day');

  const [limitPrice, setLimitPrice] = useState('');
  const [stopPrice, setStopPrice] = useState('');
  const [trailPrice, setTrailPrice] = useState('');
  const [trailPercent, setTrailPercent] = useState('');

  const modalRef = useRef();

  const handleSubmit = async () => {
    const order = {
      symbol,
      qty: Number(qty),
      side,
      order_type: orderType,
      time_in_force: timeInForce,
    };

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
      await placeOrder(order);
      onClose();
    } catch (e) {
      alert('Ошибка при создании ордера');
    }
  };

  const handleBgClick = (e) => {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  };

  return (
    <div className={`modal ${isOpen ? 'active' : ''}`} onClick={handleBgClick}>
      <div className="modal-content" ref={modalRef}>
        <h2>Create Order</h2>
        <div className="grid grid-cols-2 gap-4">
          <button onClick={() => setSide('buy')} className={side === 'buy' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-400'}>Buy</button>
          <button onClick={() => setSide('sell')} className={side === 'sell' ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-400'}>Sell</button>
        </div>

        <label>Symbol</label>
        <input type="text" value={symbol} onChange={e => setSymbol(e.target.value)} />

        <label>Order Type</label>
        <select value={orderType} onChange={e => setOrderType(e.target.value)}>
          <option value="market">Market</option>
          <option value="limit">Limit</option>
          <option value="stop">Stop</option>
          <option value="stop_limit">Stop Limit</option>
          <option value="trailing_stop">Trailing Stop</option>
        </select>

        {(orderType === 'limit' || orderType === 'stop_limit') && (
          <>
            <label>Limit Price</label>
            <input type="number" value={limitPrice} onChange={e => setLimitPrice(e.target.value)} />
          </>
        )}

        {(orderType === 'stop' || orderType === 'stop_limit') && (
          <>
            <label>Stop Price</label>
            <input type="number" value={stopPrice} onChange={e => setStopPrice(e.target.value)} />
          </>
        )}

        {orderType === 'trailing_stop' && (
          <>
            <label>Trail Price</label>
            <input type="number" value={trailPrice} onChange={e => setTrailPrice(e.target.value)} />
            <label>Trail Percent</label>
            <input type="number" value={trailPercent} onChange={e => setTrailPercent(e.target.value)} />
          </>
        )}

        <label>Quantity</label>
        <input type="number" value={qty} onChange={e => setQty(e.target.value)} />

        <label>Time in Force</label>
        <select value={timeInForce} onChange={e => setTimeInForce(e.target.value)}>
          <option value="day">DAY</option>
          <option value="gtc">GTC</option>
        </select>

        <div className="flex justify-between mt-4">
          <button className="bg-gray-300 px-4 py-2 rounded" onClick={onClose}>Cancel</button>
          <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={handleSubmit}>Submit</button>
        </div>
      </div>
    </div>
  );
};

export default OrderModal;
