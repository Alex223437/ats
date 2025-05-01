import React from 'react';
import AsideLayout from './AsideLayout';

const settingsSections = ['Profile', 'API', 'Additional'];

const AsideSettings = ({ selectedSection, setSelectedSection }) => {
  return (
    <AsideLayout title="Settings">
      <ul className="aside__list">
        {settingsSections.map((section) => (
          <li
            key={section}
            className={`aside__list-item ${selectedSection === section ? 'active' : ''}`}
            onClick={() => setSelectedSection(section)}
          >
            {section}
          </li>
        ))}
      </ul>
    </AsideLayout>
  );
};

export default AsideSettings;
