import React from 'react';
import { NavLink } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const handleFilterToggle = () => {
    window.dispatchEvent(new CustomEvent('toggle-mobile-filters'));
  };

  return (
    <nav className="main-navbar">
      <div className="navbar-left">
        {/* Botón filtros — solo visible en móvil */}
        <button
          className="navbar-filter-btn"
          onClick={handleFilterToggle}
          aria-label="Abrir filtros"
          title="Filtros"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>

        <div className="navbar-brand">
          <img src="/logo.png" alt="Zaragoza Histórica" className="navbar-logo" />
          <span className="navbar-title">Zaragoza Historica</span>
        </div>
      </div>

      <div className="navbar-links">
        <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 7L9 2L16 7V15C16 15.5523 15.5523 16 15 16H3C2.44772 16 2 15.5523 2 15V7Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
            <path d="M7 16V10H11V16" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
          </svg>
          Mapa
        </NavLink>
        <NavLink to="/contacto" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M9 5V9L12 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          Contacto
        </NavLink>
      </div>
    </nav>
  );
};
