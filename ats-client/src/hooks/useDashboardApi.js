import { useEffect, useState } from 'react';
import useApiRequest from './useApiRequest';

const useDashboardApi = (selectedStock, stocks) => {
  const [flattenedStrategies, setFlattenedStrategies] = useState([]);
  const {
    data: strategiesData,
    loading: loadingStrategies,
    request: fetchStrategies,
  } = useApiRequest();
  const { data: tickerData, loading: loadingOverview, request: fetchOverview } = useApiRequest();
  const { data: brokerInfo, loading: loadingBroker, request: fetchBroker } = useApiRequest();
  const { data: recentSignals, loading: loadingSignals, request: fetchSignals } = useApiRequest();
  const { data: chartResponse, loading: loadingMiniChart, request: fetchChart } = useApiRequest();
  const { request: fetchLastSignal } = useApiRequest();

  const miniChartData = chartResponse?.data || [];

  useEffect(() => {
    fetchStrategies({ method: 'get', url: '/strategies/active' });
    fetchBroker({ method: 'get', url: '/user/broker/check' });
    fetchSignals({ method: 'get', url: '/signals/recent' });
  }, []);

  useEffect(() => {
    if (selectedStock) {
      fetchChart({
        method: 'get',
        url: `/api/data/${selectedStock}`,
        params: { raw: true },
      });
    }
  }, [selectedStock]);

  useEffect(() => {
    if (stocks.length > 0) {
      fetchOverview({ method: 'get', url: '/stocks/overview' });
    }
  }, [stocks]);

  useEffect(() => {
    const loadSignals = async () => {
      if (!strategiesData || !Array.isArray(strategiesData)) return;

      const promises = strategiesData.flatMap((strategy) =>
        (strategy.tickers || []).map(async (ticker) => {
          try {
            const res = await fetchLastSignal({
              method: 'get',
              url: '/signals/last',
              params: { strategy_id: strategy.id, ticker },
            });
            return {
              id: `${strategy.id}_${ticker}`,
              title: strategy.title,
              ticker,
              last_signal: res?.action?.toUpperCase() || 'HOLD',
            };
          } catch {
            return {
              id: `${strategy.id}_${ticker}`,
              title: strategy.title,
              ticker,
              last_signal: 'HOLD',
            };
          }
        })
      );

      const results = await Promise.all(promises);
      setFlattenedStrategies(results);
    };

    loadSignals();
  }, [strategiesData]);

  return {
    loading: {
      strategies: loadingStrategies,
      overview: loadingOverview,
      broker: loadingBroker,
      signals: loadingSignals,
      chart: loadingMiniChart,
    },
    data: {
      flattenedStrategies,
      tickerData,
      brokerInfo: brokerInfo?.data || null,
      recentSignals,
      miniChartData,
    },
  };
};

export default useDashboardApi;
