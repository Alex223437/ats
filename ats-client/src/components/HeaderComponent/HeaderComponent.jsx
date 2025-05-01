import { Link } from 'react-router-dom';
import './HeaderComponent.scss';
import logo from '../../assets/logo/logo.png';

const HeaderComponent = ({ user, onLogout }) => {
  return (
    <header className="header">
      <Link to="/">
        <img src={logo} alt="logo" className="header__logo" />
      </Link>
      <nav className="header__navigation">
        <ul className="header__menu">
          <li className="header__menu-item">
            <Link to="/" className="header__menu-link">
              Dashboard
            </Link>
          </li>
          <li className="header__menu-item">
            <Link to="/trades" className="header__menu-link">
              Trades
            </Link>
          </li>
          <li className="header__menu-item">
            <Link to="/strategy" className="header__menu-link">
              Strategy
            </Link>
          </li>
          <li className="header__menu-item">
            <Link to="/analytics" className="header__menu-link">
              Analytics
            </Link>
          </li>
          <li className="header__menu-item">
            <Link to="/settings" className="header__menu-link">
              Settings
            </Link>
          </li>
          {user ? (
            <li className="header__menu-user">
              <span className="header__user">Hello, {user.username || user.email}!</span>
              <button className="header__logout" onClick={onLogout}>
                Logout
              </button>
            </li>
          ) : (
            <>
              <li className="header__menu-item">
                <Link className="header__link" to="/register">
                  Sign up
                </Link>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default HeaderComponent;
