import useApiRequest from './useApiRequest';

const useAnalyticsApi = () => {
  const overview = useApiRequest(false);
  const strategiesPnl = useApiRequest(false);
  const topTickers = useApiRequest(false);
  const equityCurve = useApiRequest(false);
  const trades = useApiRequest(false);

  const getParams = (filters) => {
    const params = {};
    if (filters.strategy_id) params.strategy_id = filters.strategy_id;
    if (filters.ticker) params.ticker = filters.ticker;
    if (filters.startDate && !isNaN(new Date(filters.startDate))) {
      params.start_date = new Date(filters.startDate).toISOString();
    }
    if (filters.endDate && !isNaN(new Date(filters.endDate))) {
      params.end_date = new Date(filters.endDate).toISOString();
    }
    return params;
  };

  const fetchOverview = (filters) =>
    overview.request({ method: 'GET', url: '/analytics/overview', params: getParams(filters) });

  const fetchStrategiesPnl = (filters) =>
    strategiesPnl.request({
      method: 'GET',
      url: '/analytics/strategies-pnl',
      params: getParams(filters),
    });

  const fetchTopTickers = (filters, limit = 5) =>
    topTickers.request({
      method: 'GET',
      url: '/analytics/top-tickers',
      params: { ...getParams(filters), limit },
    });

  const fetchEquityCurve = (filters) =>
    equityCurve.request({
      method: 'GET',
      url: '/analytics/equity-curve',
      params: getParams(filters),
    });

  const fetchTrades = (filters) =>
    trades.request({ method: 'GET', url: '/analytics/trades', params: getParams(filters) });

  return {
    overview,
    strategiesPnl,
    topTickers,
    equityCurve,
    trades,
    fetchOverview,
    fetchStrategiesPnl,
    fetchTopTickers,
    fetchEquityCurve,
    fetchTrades,
  };
};

export default useAnalyticsApi;
