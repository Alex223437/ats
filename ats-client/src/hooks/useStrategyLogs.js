import useApiRequest from './useApiRequest';

const useStrategyLogs = () => {
  const request = useApiRequest();

  const fetchStrategyLogs = (strategyId, limit = 20) =>
    request.request({
      method: 'get',
      url: `/strategies/${strategyId}/logs`,
      params: { limit },
    });

  return { fetchStrategyLogs, loading: request.loading };
};

export default useStrategyLogs;
