import api from './apiService'; // это твой axios instance

/**
 * Запуск бэктеста с указанными параметрами
 * @param {Object} payload
 * @param {number} payload.strategy_id
 * @param {string} payload.ticker
 * @param {Object} payload.parameters
 * @param {string} payload.start_date — ISO строка
 * @param {string} payload.end_date — ISO строка
 * @returns {Promise<Object>} — объект с метриками и точками сделок
 */
export const runBacktest = async (payload) => {
  try {
    const response = await api.post('/backtest/run', payload);
    return response.data;
  } catch (err) {
    console.error('❌ Ошибка при запуске бэктеста:', err.response?.data || err.message);
    throw err;
  }
};
