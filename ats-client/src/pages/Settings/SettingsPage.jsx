import './SettingsPage.scss';
import BrokerIntegrationCard from '@/components/SettingsComponent/BrokerIntegrationCard';
import TradingPreferencesCard from '@/components/SettingsComponent/TradingPreferencesCard';
import NotificationSettingsCard from '@/components/SettingsComponent/NotificationSettingsCard';
import AccountInfoCard from '@/components/SettingsComponent/AccountInfoCard';
import SunIcon from '@/assets/svg/sun.svg?react';

const SettingsPage = () => {
  return (
    <div className="settings-grid">
      <div className="column">
        <aside className="settings-sidebar">
          <h2>Settings</h2>
          <p>
            This is your control center for trading preferences, broker integrations, alerts and profile settings.
            Configure once, trade with confidence.
          </p>
          <div className="app-version">Automatic Trading System v0.1.0</div>
        </aside>
        <AccountInfoCard />
        
      </div>
      <div className="column">
        <BrokerIntegrationCard />
        <NotificationSettingsCard />
      </div>
      <div className="column">
        <TradingPreferencesCard />
        <SunIcon className="settings-icon"/>
      </div>
      
    </div>
  );
};

export default SettingsPage;