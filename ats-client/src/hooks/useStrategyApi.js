import { useState } from 'react';
import useApiRequest from './useApiRequest';

export const useStrategyApi = () => {
  const [strategies, setStrategies] = useState([]);

  const fetchAll = useApiRequest();
  const create = useApiRequest();
  const update = useApiRequest();
  const remove = useApiRequest();
  const fetchActive = useApiRequest();
  const disable = useApiRequest();
  const enable = useApiRequest();
  const setTickers = useApiRequest();
  const fetchTickers = useApiRequest();
  const train = useApiRequest();
  const deleteModel = useApiRequest();

  const fetchStrategies = async () => {
    const data = await fetchAll.request({ method: 'get', url: '/strategies' });

    const enriched = await Promise.all(
      data.map(async (strategy) => {
        if (!strategy.is_enabled || !strategy.tickers?.length) {
          return strategy;
        }
        const last_signals = {};

        const signalFetches = strategy.tickers.map(async (ticker) => {
          try {
            const res = await fetchAll.request({
              method: 'get',
              url: '/signals/last',
              params: { strategy_id: strategy.id, ticker },
            });

            last_signals[ticker] = res?.action?.toUpperCase() || 'HOLD';
          } catch (err) {
            console.error('Error fetching last signal:', err);
            last_signals[ticker] = 'HOLD';
          }
        });

        await Promise.all(signalFetches);

        return {
          ...strategy,
          last_signals,
        };
      })
    );

    setStrategies(enriched);
    return enriched;
  };

  return {
    fetchStrategies,
    refreshStrategies: fetchStrategies,
    createStrategy: (strategy) =>
      create.request({ method: 'post', url: '/strategies', data: strategy }),
    updateStrategy: (strategyId, strategy) =>
      update.request({ method: 'put', url: `/strategies/${strategyId}`, data: strategy }),
    deleteStrategy: (strategyId) =>
      remove.request({ method: 'delete', url: `/strategies/${strategyId}` }),
    getActiveStrategies: () => fetchActive.request({ method: 'get', url: '/strategies/active' }),
    disableStrategy: (strategyId) =>
      disable.request({ method: 'put', url: `/strategies/${strategyId}/disable` }),
    enableStrategy: (strategyId) =>
      enable.request({ method: 'put', url: `/strategies/${strategyId}/enable` }),

    setStrategyTickers: (strategyId, tickers) =>
      setTickers.request({
        method: 'post',
        url: `/strategies/${strategyId}/tickers`,
        data: { tickers },
      }),
    trainStrategyModel: (strategyId) =>
      train.request({ method: 'post', url: `/strategies/${strategyId}/train` }),
    fetchStrategyTickers: (strategyId) =>
      fetchTickers.request({ method: 'get', url: `/strategies/${strategyId}/tickers` }),
    deleteTrainedModel: (strategyId) =>
      deleteModel.request({ method: 'delete', url: `/strategies/${strategyId}/model` }),

    strategies,
    loading: {
      fetch: fetchAll.loading,
      create: create.loading,
      update: update.loading,
      remove: remove.loading,
      active: fetchActive.loading,
      disable: disable.loading,
      enable: enable.loading,
      setTickers: setTickers.loading,
      fetchTickers: fetchTickers.loading,
      train: train.loading,
    },
  };
};

export default useStrategyApi;
