import useApiRequest from './useApiRequest';

const useBacktestApi = () => {
  const run = useApiRequest(false);
  const fetchById = useApiRequest(false);

  const runBacktest = (data) =>
    run.request({
      method: 'POST',
      url: '/backtest/run',
      data,
    });

  const getBacktestResult = (id) =>
    fetchById.request({
      method: 'GET',
      url: `/backtest/results/${id}`,
    });

  return {
    run,
    fetchById,
    runBacktest,
    getBacktestResult,
  };
};

export default useBacktestApi;
