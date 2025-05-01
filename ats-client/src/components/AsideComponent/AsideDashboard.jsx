import React, { useState, useEffect } from 'react';
import AsideLayout from './AsideLayout';
import { fetchUserStocks, addUserStock, removeUserStock } from '../../services/stockService';

const AsideDashboard = ({ stocks, setStocks, selectedStock, setSelectedStock }) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [newStock, setNewStock] = useState('');

  useEffect(() => {
    const loadStocks = async () => {
      const userStocks = await fetchUserStocks();
      setStocks(userStocks);
    };
    loadStocks();
  }, []);

  const toggleForm = () => setIsFormOpen(!isFormOpen);

  const handleAddStock = async (e) => {
    e.preventDefault();
    if (newStock.trim() && !stocks.includes(newStock)) {
      await addUserStock(newStock);
      setStocks([...stocks, newStock]);
      setNewStock('');
      setIsFormOpen(false);
    }
  };

  const handleRemoveStock = async (ticker) => {
    await removeUserStock(ticker);
    setStocks(stocks.filter((stock) => stock !== ticker));
  };

  return (
    <AsideLayout title="Stocks">
      <ul className="aside__list">
        {stocks.map((stock, index) => (
          <li
            key={index}
            className={`aside__list-item ${selectedStock === stock ? 'active' : ''}`}
            onClick={() => setSelectedStock(stock)}
          >
            <span>{stock}</span>
            <button className='aside__delete' onClick={() => handleRemoveStock(stock)}>x</button>
          </li>
        ))}
      </ul>

      <button className="aside__btn" onClick={toggleForm}>
        {isFormOpen ? '×' : '+'}
      </button>

      {isFormOpen && (
        <form className='aside__form' onSubmit={handleAddStock}>
          <input
            type="text"
            placeholder="Enter ticker"
            value={newStock}
            onChange={(e) => setNewStock(e.target.value)}
          />
          <button className='aside__form__submit' type="submit">Add</button>
        </form>
      )}
    </AsideLayout>
  );
};

export default AsideDashboard;
