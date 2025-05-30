import useApiRequest from './useApiRequest';

const useSettingsApi = () => {
  const {
    request: fetchUserSettings,
    data: userSettings,
    loading: loadingUser,
    error: errorUser,
  } = useApiRequest(false);

  const {
    request: fetchNotifications,
    data: notificationSettings,
    loading: loadingNotifications,
    error: errorNotifications,
  } = useApiRequest(false);

  const {
    request: fetchBroker,
    data: brokerData,
    loading: loadingBroker,
    error: errorBroker,
  } = useApiRequest(false);

  const {
    request: fetchTradingPrefs,
    data: tradingPreferences,
    loading: loadingTradingPrefs,
    error: errorTradingPrefs,
  } = useApiRequest(false);

  const { request: updateNotifications, loading: updatingNotifications } = useApiRequest(false);

  const { request: updateUserProfile, loading: updatingUser } = useApiRequest(false);

  const { request: updateBroker, loading: updatingBroker } = useApiRequest(false);

  const { request: disconnectBroker, loading: disconnectingBroker } = useApiRequest(false);

  const { request: updateTradingPrefs, loading: updatingTradingPrefs } = useApiRequest(false);

  return {
    fetchUserSettings: () => fetchUserSettings({ method: 'get', url: '/user/settings' }),
    updateUserProfile: (data) =>
      updateUserProfile({ method: 'put', url: '/user/settings/profile', data }),
    userSettings,
    loadingUser,
    errorUser,

    fetchNotifications: () => fetchNotifications({ method: 'get', url: '/settings/notifications' }),
    updateNotifications: (data) =>
      updateNotifications({ method: 'post', url: '/settings/notifications', data }),
    notificationSettings,
    loadingNotifications,
    errorNotifications,
    updatingNotifications,

    fetchBroker: (broker = 'alpaca') =>
      fetchBroker({ method: 'get', url: `/user/brokers/${broker}/check` }),
    updateBroker: (data) => updateBroker({ method: 'post', url: '/user/brokers', data }),
    disconnectBroker: (broker) =>
      disconnectBroker({ method: 'delete', url: `/user/brokers/${broker}` }),
    brokerData,
    loadingBroker,
    errorBroker,
    updatingBroker,
    disconnectingBroker,

    fetchTradingPreferences: () => fetchTradingPrefs({ method: 'get', url: '/settings/trading' }),
    updateTradingPreferences: (data) =>
      updateTradingPrefs({ method: 'post', url: '/settings/trading', data }),
    tradingPreferences,
    loadingTradingPrefs,
    errorTradingPrefs,
    updatingTradingPrefs,
  };
};

export default useSettingsApi;
