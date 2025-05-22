import { useEffect, useState } from 'react';
import useApiRequest from './useApiRequest';

const useStrategiesAndTickers = () => {
  const { request: fetchStrategies } = useApiRequest(false);
  const { request: fetchTickers } = useApiRequest(false);

  const [strategies, setStrategies] = useState([]);
  const [tickers, setTickers] = useState([]);

  useEffect(() => {
    fetchStrategies({ method: 'GET', url: '/strategies' }).then(setStrategies);
    fetchTickers({ method: 'GET', url: '/users/me/stocks' }).then(setTickers);
  }, []);

  return {
    strategies,
    tickers,
  };
};

export default useStrategiesAndTickers;
