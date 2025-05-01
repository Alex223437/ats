import api from './apiService';

export const getUserSettings = async () => {
  try {
    const response = await api.get('/user/settings');
    return response.data;
  } catch (error) {
    console.error('Error fetching user settings:', error.response?.data || error.message);
    return null;
  }
};

export const updateUserProfile = async (settings) => {
  try {
    const response = await api.put('/user/settings/profile', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error.response?.data || error.message);
    return { success: false };
  }
};

export const updateBrokerSettings = async (settings) => {
  try {
    const response = await api.put('/user/settings/broker', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating broker settings:', error.response?.data || error.message);
    return { success: false };
  }
};

export const checkBrokerConnection = async () => {
  try {
    const response = await api.get('/user/broker/check');
    return response.data;
  } catch (error) {
    return {
      connected: false,
      error: error.response?.data?.detail || 'Unknown error',
    };
  }
};

export const disconnectBroker = async () => {
  try {
    const response = await api.delete('/user/broker');
    return response.data;
  } catch (error) {
    console.error('Error disconnecting broker:', error.response?.data || error.message);
    return { success: false };
  }
};
