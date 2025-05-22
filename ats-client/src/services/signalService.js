import api from './apiService';

export const fetchRecentSignals = async () => {
  const res = await api.get('/signals/recent');
  return res.data;
};
