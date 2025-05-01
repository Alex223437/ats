import React, { useState, useEffect } from 'react';
import AsideDashboard from '../components/AsideComponent/AsideDashboard';
import ChartComponent from '../components/ChartComponent/ChartComponent';
import { fetchIndicators } from '../services/stockService';
import './AnalyticsPage.scss';

const AnalyticsPage = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [indicators, setIndicators] = useState(null);

  useEffect(() => {
    const loadIndicators = async () => {
      if (!selectedStock) return;
      const data = await fetchIndicators(selectedStock);
      setIndicators(data);
    };

    loadIndicators();
  }, [selectedStock]);

  return (
    <>
      <AsideDashboard
        stocks={stocks}
        setStocks={setStocks}
        selectedStock={selectedStock}
        setSelectedStock={setSelectedStock}
      />

      {selectedStock ? (
        <div className="analytics__main">
          <ChartComponent ticker={selectedStock} />
          
          {indicators && (
            <table className="indicators-table">
              <thead>
                <tr>
                  <th>Indicator</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(indicators).map(([key, val]) => (
                  <tr key={key}>
                    <td>{key}</td>
                    <td>{val}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <div className="placeholder">Select a stock to view analytics</div>
      )}
    </>
  );
};

export default AnalyticsPage;