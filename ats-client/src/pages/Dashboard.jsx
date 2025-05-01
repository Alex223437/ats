import AsideDashboard from "../components/AsideComponent/AsideDashboard";
import ChartComponent from "../components/ChartComponent/ChartComponent";
import { fetchUserStocks } from '@/services/stockService';
import { useEffect, useState } from "react";
const Dashboard = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');

  useEffect(() => {
    const loadStocks = async () => {
      const userStocks = await fetchUserStocks();
      setStocks(userStocks);
      if (userStocks.length > 0) {
        setSelectedStock(userStocks[0]); // выбираем первый тикер
      }
    };
  
    loadStocks();
  }, []);
  return (
    <>

      <AsideDashboard
        stocks={stocks}
        setStocks={setStocks}
        selectedStock={selectedStock}
        setSelectedStock={setSelectedStock}
      />
      <ChartComponent
        ticker={selectedStock}
        setStocks={setStocks}
        selectedStock={selectedStock}
        setSelectedStock={setSelectedStock}
      />
    </>
  );
}
export default Dashboard;