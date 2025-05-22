import { NavLink } from 'react-router-dom';
import './HeaderComponent.scss';
import logo from '../../assets/logo/logo.png';
import { toast } from 'react-hot-toast';

const HeaderComponent = ({ user, onLogout }) => {

  const handleLogout = async () => {
    try {
      await onLogout();
      toast.success('You have been logged out');
    } catch (err) {
      toast.error('Failed to logout');
    }
  };

  return (
    <header className="header">
      <NavLink to="/">
        <img src={logo} alt="logo" className="header__logo" />
      </NavLink>
      <nav className="header__navigation">
        <ul className="header__menu">
          <li className="header__menu-item">
            <NavLink to="/" className={({ isActive }) =>
              `header__menu-link${isActive ? ' active' : ''}`
            }>
              Dashboard
            </NavLink>
          </li>
          <li className="header__menu-item">
            <NavLink to="/trades" className={({ isActive }) =>
              `header__menu-link${isActive ? ' active' : ''}`
            }>
              Trades
            </NavLink>
          </li>
          <li className="header__menu-item">
            <NavLink to="/strategy" className={({ isActive }) =>
              `header__menu-link${isActive ? ' active' : ''}`
            }>
              Strategy
            </NavLink>
          </li>
          <li className="header__menu-item">
            <NavLink to="/analytics" className={({ isActive }) =>
              `header__menu-link${isActive ? ' active' : ''}`
            }>
              Analytics
            </NavLink>
          </li>
          <li className="header__menu-item">
            <NavLink to="/backtest" className={({ isActive }) =>
              `header__menu-link${isActive ? ' active' : ''}`
            }>
              Backtest
            </NavLink>
          </li>
          <li className="header__menu-item">
            <NavLink to="/settings"className={({ isActive }) =>
                `header__menu-link${isActive ? ' active' : ''}`
              }>
              Settings
            </NavLink>
          </li>
          {user ? (
            <li className="header__menu-user">
              <span className="header__user">Hello, {user.username || user.email}!</span>
              <button className="header__logout" onClick={handleLogout}>
                Logout
              </button>
            </li>
          ) : (
            <>
              <li className="header__menu-item">
                <NavLink className="header__link" to="/register">
                  Sign up
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default HeaderComponent;
