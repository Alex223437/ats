import React from 'react';
import './AsideLayout.scss';

const AsideLayout = ({ title, children }) => {
  return (
    <aside className="aside">
      <h2 className="aside__title">{title}</h2>
      <nav className="aside__navigation">{children}</nav>
    </aside>
  );
};

export default AsideLayout;
