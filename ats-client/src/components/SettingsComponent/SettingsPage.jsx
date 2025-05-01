import React from 'react';
import SettingsProfile from './SettingsProfile';
import SettingsAPI from './SettingsAPI';
import SettingsAdditional from './SettingsAdditional';
import './SettingsPage.scss';

const SettingsPage = ({ selectedSection }) => {
  const renderSection = () => {
    switch (selectedSection) {
      case 'Profile':
        return <SettingsProfile />;
      case 'API':
        return <SettingsAPI />;
      case 'Additional':
        return <SettingsAdditional />;
      default:
        return <SettingsProfile />;
    }
  };

  return <div className="settings-container">{renderSection()}</div>;
};

export default SettingsPage;
