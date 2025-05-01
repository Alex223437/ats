import api from './apiService';

export const getTrades = async () => {
  try {
    const response = await api.get('/trades');
    return response.data;
  } catch (error) {
    console.error('Error fetching trades:', error.response?.data || error.message);
    return [];
  }
};

export const getOrders = async () => {
  try {
    const response = await api.get('/orders');
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error.response?.data || error.message);
    return [];
  }
};

export const cancelOrder = async (orderId) => {
  try {
    await api.delete(`/orders/${orderId}`);
  } catch (error) {
    console.error('Error canceling order:', error.response?.data || error.message);
  }
};

export const closePosition = async (symbol) => {
  try {
    await api.delete(`/trades/${symbol}`);
  } catch (error) {
    console.error('Error closing position:', error.response?.data || error.message);
  }
};

export const placeOrder = async (orderData) => {
  try {
    const response = await api.post('/orders', orderData);
    return response.data;
  } catch (error) {
    console.error('Error placing order:', error.response?.data || error.message);
    throw error;
  }
};
