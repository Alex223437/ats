import { useState, useCallback } from 'react';
import api from '../services/apiService';

const useApiRequest = (initialLoading = true) => {
  const [loading, setLoading] = useState(initialLoading);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const request = useCallback(async (config) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await api(config);
      setData(res.data);
      return res.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Unexpected error';
      setError(message);
      console.error('API Error:', message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, error, loading, request };
};

export default useApiRequest;
