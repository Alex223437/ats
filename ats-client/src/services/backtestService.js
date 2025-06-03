import api from './apiService';

export const runBacktest = async (payload) => {
  try {
    const response = await api.post('/backtest/run', payload);
    return response.data;
  } catch (err) {
    console.error('Error on backtest: ', err.response?.data || err.message);
    throw err;
  }
};
