import api from './apiService';

export const fetchStockData = async (ticker, strategyId = null, raw = false) => {
  try {
    const params = {};
    if (strategyId) params.strategy_id = strategyId;
    if (raw) params.raw = true;

    const response = await api.get(`/api/data/${ticker}`, { params });
    return response.data.data;
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
    return [];
  }
};

export const fetchUserStocks = async () => {
  try {
    const response = await api.get('/users/me/stocks');
    return response.data.stocks;
  } catch (error) {
    console.error('Error fetching user stocks:', error.response?.data || error.message);
    return [];
  }
};

export const addUserStock = async (ticker) => {
  try {
    await api.post('/users/me/stocks/add', null, {
      params: { ticker },
    });
  } catch (error) {
    console.error('Error adding stock:', error.response?.data || error.message);
  }
};

export const removeUserStock = async (ticker) => {
  try {
    await api.delete('/users/me/stocks/remove', {
      params: { ticker },
    });
  } catch (error) {
    console.error('Error removing stock:', error.response?.data || error.message);
  }
};

export const fetchIndicators = async (ticker) => {
  try {
    const response = await api.get(`/api/indicators/${ticker}`);
    return response.data;
  } catch (error) {
    console.error('Error indicators loading:', error);
    return null;
  }
};

export const fetchTickerOverview = async () => {
  const response = await api.get('/stocks/overview', { withCredentials: true });
  return response.data;
};
