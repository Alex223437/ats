import AsideDashboard from "../components/AsideComponent/AsideDashboard";
import DashboardOverview from "../components/DashboardOverview/DashboardOverview";
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
        setSelectedStock(userStocks[0]); 
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
      <DashboardOverview selectedStock={selectedStock} stocks={stocks}></DashboardOverview>
    </>
   
  );
}
export default Dashboard;
