import api from './apiService';

export const fetchStockData = async (ticker, strategyId = null) => {
  try {
    const params = strategyId ? { strategy_id: strategyId } : {};
    const response = await api.get(`/api/data/${ticker}`, { params });
    return response.data.data;
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
    return [];
  }
};

// Fetch user stocks
export const fetchUserStocks = async () => {
  const token = localStorage.getItem('token');
  if (!token) return [];

  try {
    const response = await api.get('/users/me/stocks', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.stocks;
  } catch (error) {
    console.error('Error fetching user stocks:', error.response?.data || error.message);
    return [];
  }
};

// Add a stock
export const addUserStock = async (ticker) => {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    await api.post('/users/me/stocks/add', null, {
      params: { ticker },
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (error) {
    console.error('Error adding stock:', error.response?.data || error.message);
  }
};

// Remove a stock
export const removeUserStock = async (ticker) => {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    await api.delete('/users/me/stocks/remove', {
      params: { ticker },
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (error) {
    console.error('Error removing stock:', error.response?.data || error.message);
  }
};

export const fetchAiPrediction = async (ticker) => {
  try {
    const response = await api.get(`/ai/predict/${ticker}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при загрузке AI предсказаний:', error);
    return [];
  }
};

export const fetchIndicators = async (ticker) => {
  try {
    const response = await api.get(`/api/indicators/${ticker}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка загрузки индикаторов:', error);
    return null;
  }
};
