import React, { useEffect, useState } from 'react';
import AsideLayout from './AsideLayout';
import { addUserStock, removeUserStock } from '@/services/stockService';
import allTickers from '@/data/tickers.json';
import { toast } from 'react-hot-toast';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import useApiRequest from '@/hooks/useApiRequest';

const AsideDashboard = ({ stocks, setStocks, selectedStock, setSelectedStock }) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [newStock, setNewStock] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const { data, loading, error, request } = useApiRequest();

  useEffect(() => {
    request({ method: 'GET', url: '/users/me/stocks' })
      .then((res) => setStocks(res.stocks || []))
      .catch(() => toast.error('Failed to load tickers'));
  }, []);

  const toggleForm = () => {
    setIsFormOpen(!isFormOpen);
    setNewStock('');
    setSuggestions([]);
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    const ticker = newStock.toUpperCase().trim();
    if (!ticker) return;

    if (stocks.includes(ticker)) return toast.error(`Ticker ${ticker} already added.`);
    if (!allTickers.find((t) => t.ticker === ticker)) return toast.error(`Ticker ${ticker} not found.`);

    try {
      await addUserStock(ticker);
      setStocks((prev) => [...prev, ticker]);
      setNewStock('');
      setIsFormOpen(false);
      toast.success(`Ticker ${ticker} added!`);
    } catch {
      toast.error('Error adding ticker');
    }
  };

  const handleRemoveStock = async (ticker) => {
    await removeUserStock(ticker);
    setStocks((prev) => prev.filter((t) => t !== ticker));
    toast.success(`Ticker ${ticker} removed.`);
  };

  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setNewStock(value);
    if (value.length >= 2) {
      const filtered = allTickers.filter((t) => t.ticker.startsWith(value)).slice(0, 10);
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
  };

  const selectSuggestion = (ticker) => {
    setNewStock(ticker);
    setSuggestions([]);
  };

  return (
    <AsideLayout title="Stocks">
      {loading ? (
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: '10px', color: '#94a3b8' }}>Loading your tickers...</p>
        </div>
      ) : (
        <>
          <ul className="aside__list">
            {stocks.map((stock, index) => (
              <li
                key={index}
                className={`aside__list-item ${selectedStock === stock ? 'active' : ''}`}
                onClick={() => setSelectedStock(stock)}
              >
                <span>{stock}</span>
                <button className="aside__delete" onClick={() => handleRemoveStock(stock)}>x</button>
              </li>
            ))}
          </ul>

          <button className="aside__btn" onClick={toggleForm}>
            {isFormOpen ? '×' : '+'}
          </button>

          {isFormOpen && (
            <form className="aside__form" onSubmit={handleAddStock}>
              <input
                type="text"
                placeholder="Enter ticker"
                value={newStock}
                onChange={handleInputChange}
                autoComplete="off"
              />
              <button className="aside__form__submit" type="submit">Add</button>

              {suggestions.length > 0 && (
                <ul className="suggestions-list">
                  {suggestions.map((s) => (
                    <li key={s.ticker} onClick={() => selectSuggestion(s.ticker)}>
                      <strong>{s.ticker}</strong> — {s.name}
                    </li>
                  ))}
                </ul>
              )}
            </form>
          )}
        </>
      )}
    </AsideLayout>
  );
};

export default AsideDashboard;