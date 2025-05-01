import api from './apiService';

export const fetchStrategies = async () => {
  try {
    const response = await api.get('/strategies');
    return response.data;
  } catch (error) {
    console.error('Error fetching strategies:', error);
    return [];
  }
};

export const createStrategy = async (strategy) => {
  try {
    console.log('Creating strategy:', strategy);
    const response = await api.post('/strategies', strategy);
    return response.data;
  } catch (error) {
    console.error('Error creating strategy:', error);
  }
};

export const updateStrategy = async (strategyId, strategy) => {
  try {
    const response = await api.put(`/strategies/${strategyId}`, strategy);
    return response.data;
  } catch (error) {
    console.error('Error updating strategy:', error);
  }
};

export const deleteStrategy = async (strategyId) => {
  try {
    await api.delete(`/strategies/${strategyId}`);
  } catch (error) {
    console.error('Error deleting strategy:', error);
  }
};

export const getActiveStrategies = async () => {
  try {
    const response = await api.get('/strategies/active');
    return response.data;
  } catch (error) {
    console.error('Error fetching active strategies:', error);
    return [];
  }
};

export const disableStrategy = async (strategyId) => {
  try {
    await api.put(`/strategies/${strategyId}/disable`);
  } catch (error) {
    console.error('Error disabling strategy:', error);
  }
};
