import React from 'react';
import './DashboardOverview.scss';

const OverviewCard = ({ title, children, className = '' }) => {
  return (
    <div className={`overview-card ${className}`}>
      {title && <h3 className="overview-card__title">{title}</h3>}
      <div className="overview-card__content">{children}</div>
    </div>
  );
};

export default OverviewCard;
