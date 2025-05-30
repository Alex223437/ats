import { useState, useEffect, useRef } from 'react';
import useBrokerApi from './useBrokerApi';
import useApiRequest from './useApiRequest';

const useTradingApi = (broker = 'alpaca') => {
  const { checkBroker } = useBrokerApi();

  const [connected, setConnected] = useState(null);
  const [brokerError, setBrokerError] = useState('');
  const [initialLoaded, setInitialLoaded] = useState(false);

  const hasLoaded = useRef(false);

  const { data: orders, loading: loadingOrders, request: fetchOrders } = useApiRequest();

  const { data: positions, loading: loadingPositions, request: fetchPositions } = useApiRequest();

  useEffect(() => {
    if (hasLoaded.current) return;
    hasLoaded.current = true;

    const load = async () => {
      try {
        const res = await checkBroker(broker);
        if (res.connected) {
          setConnected(true);
          await Promise.all([
            fetchOrders({ method: 'get', url: '/orders' }),
            fetchPositions({ method: 'get', url: '/trades' }),
          ]);
        } else {
          setConnected(false);
          setBrokerError(res.error || 'Broker not connected');
        }
      } catch {
        setConnected(false);
        setBrokerError('Failed to verify broker connection');
      } finally {
        setInitialLoaded(true);
      }
    };

    load();
  }, []);

  return {
    connected,
    brokerError,
    initialLoaded,
    orders: orders || [],
    positions: positions || [],
    loadingOrders,
    loadingPositions,
    fetchOrders,
    fetchPositions,
  };
};

export default useTradingApi;
