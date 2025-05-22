import { useCallback } from 'react';
import useApiRequest from './useApiRequest';

export const useAuth = () => {
  const { request, loading, error, data } = useApiRequest(false);

  const registerUser = useCallback(
    async (formData) => {
      return await request({
        url: '/register',
        method: 'POST',
        data: formData,
      });
    },
    [request]
  );

  const loginUser = useCallback(
    async (email, password) => {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      await request({
        url: '/token',
        method: 'POST',
        data: formData,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      // ✅ кука установлена сервером, токен хранить не нужно
    },
    [request]
  );

  const getCurrentUser = useCallback(async () => {
    try {
      return await request({ url: '/users/me' });
    } catch (err) {
      return null;
    }
  }, [request]);

  const logoutUser = useCallback(async () => {
    await request({ url: '/logout', method: 'POST' });
  }, [request]);

  return {
    registerUser,
    loginUser,
    getCurrentUser,
    logoutUser,
    loading,
    error,
    data,
  };
};
