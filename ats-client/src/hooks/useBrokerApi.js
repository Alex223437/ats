import useApiRequest from './useApiRequest';

export const useBrokerApi = () => {
  const update = useApiRequest(false);
  const check = useApiRequest(false);
  const disconnect = useApiRequest(false);

  const updateBroker = async (params) => {
    return await update.request({
      method: 'POST',
      url: '/user/brokers',
      data: params,
    });
  };

  const checkBroker = async (broker = 'alpaca') => {
    return await check.request({
      method: 'GET',
      url: `/user/brokers/${broker}/check`,
    });
  };

  const disconnectBroker = async (broker = 'alpaca') => {
    return await disconnect.request({
      method: 'DELETE',
      url: `/user/brokers/${broker}`,
    });
  };

  return {
    updateBroker,
    checkBroker,
    disconnectBroker,
    updateState: update,
    checkState: check,
    disconnectState: disconnect,
  };
};

export default useBrokerApi;
